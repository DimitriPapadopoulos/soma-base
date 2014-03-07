# -*- coding: utf-8 -*-
import os
from socket import getfqdn
from datetime import datetime as datetime
from copy import deepcopy
import json

try:
    import traits.api as traits
    from traits.api import (ListStr, HasTraits, File, Float, Instance,
                            Enum, Str, Directory, Dict)
    from traits.trait_base import _Undefined
except ImportError:
    import enthought.traits.api as traits
    from enthought.traits.api import (ListStr, HasTraits, File, Float,
                                      Instance, Enum, Str, Directory, Dict)

from soma.controller import Controller
from soma.controller import trait_ids
from soma.utils import (LateBindingProperty, get_tool_version)

try:
    from nipype.interfaces.base import InterfaceResult
except:
    class InterfaceResult(object):
        pass


class Process(Controller):
    """ TODO
    """
    def __init__(self):
        """ Init the process class.

        In a process instance it is possible to define QC process(es)
        that will be used to evaluate the quality of the result.

        It is also possible to add viewers to check the input, output, or
        QC data.
        """
        # inheritance
        super(Process, self).__init__()

        # intern identifiers
        self.name = self.__class__.__name__
        self.id = self.__class__.__module__ + '.' + self.name

        # tools around the current process
        self.viewers = {}
        self.qc_processes = {}

        # runtime information
        self.runtime = None

        # log file name
        self.log_file = None

        # Add trait to store processing output directory
        super(Process, self).add_trait("output_directory",
                                       Directory(_Undefined(),
                                       exists=True, optional=True))

        # Add trait to store the execution information
        #super(Process, self).add_trait("exec_info",
                                       #Dict(output=True,
                                            #optional=True))
        self.exec_info = {}

    ##############
    # Members    #
    ##############

    def __call__(self):
        """ Execute the Process

        Returns
        -------
        results:  ProcessResult object
            Contains all execution information
        """
        # Get class
        process = self.__class__

        # Execution report
        runtime = {
            "start_time": datetime.isoformat(datetime.utcnow()),
            "cwd": os.getcwd(),
            "returncode": None,
            "environ": deepcopy(os.environ.data),
            "end_time": None,
            "hostname": getfqdn(),
        }

        # Call
        returncode = self._run_process()

        # End timer
        runtime["end_time"] = datetime.isoformat(datetime.utcnow())

        # Get dependencies' versions
        versions = {
            "soma": get_tool_version("soma"),
        }
        if "_nipype_interface" in dir(self):
            versions["nipype"] = get_tool_version("nipype")
            interface_name = self._nipype_interface.__module__.split(".")[2]
            versions[interface_name] = self._nipype_interface.version
        runtime["versions"] = versions

        # If run a Nipype process, get more informations
        if isinstance(returncode, InterfaceResult):
            process = returncode.interface
            if "cmd_line" in dir(returncode.runtime):
                runtime["cmd_line"] = returncode.runtime.cmdline
            runtime["stderr"] = returncode.runtime.stderr
            runtime["stdout"] = returncode.runtime.stdout
            runtime["cwd"] = returncode.runtime.cwd
            runtime["returncode"] = returncode.runtime.returncode

        # Result
        results = ProcessResult(process, runtime, self.get_inputs(),
                                self.get_outputs())

        # Sotre execution informations
        self.exec_info = self._get_log(results)
        results.outputs["exec_info"] = self.exec_info

        return results

    def _run_process(self):
        """ Process function that will be call.
        This function must be defined in derived classes.
        """
        raise NotImplementedError()

#    def auto_nipype_process_qc(self):
#        """ From a nipype process instance call automatically
#        quality control tools
#        """
#        pass
#        #interface_name = self._nipype_interface.__class__.__name__
#        #qc_id = ("casper.use_cases.qc."
#        #         "{0}QualityCheck".format(interface_name))
#        #qc_instance = get_instance(qc_id,
#        #                      nipype_interface=self._nipype_interface)
#        #self.qc_processes["automatic"] = qc_instance

#==============================================================================
#
#     def call_viewer(self, controller_widget, name):
#         viewer, kwargs = self.viewers[name]
#         if not kwargs:
#             liste = []
#             liste.append(getattr(controller_widget.controller, name))
#             p = GlobalNaming().get_object(viewer)(*liste)
#         else:
#             dico_parameter = {}
#             #dico_parameter[name]=value
#             #get all traits name of the process
#             trait_of_process = controller_widget.controller.user_traits(). \
#                                keys()
#             #Get parameters in the kwargs and complete value of traits needed
#             for key, value in kwargs.iteritems():
#                 dico_parameter[key] = value
#                 if value in trait_of_process:
#                     dico_parameter[key] = getattr(
#                         controller_widget.controller,
#                         value)
#             p = GlobalNaming().get_object(viewer)(**dico_parameter)
#         return p()
#==============================================================================

    ##############
    # Properties #
    ##############

    def get_input_spec(self):
        """ Pipeline input specification

        Returns
        -------
        outputs: str
            a dictionary with all the input Plugs' specifications
        """
        output = "\nINPUT SPECIFICATIONS\n\n"
        for trait_name, trait in self.user_traits().iteritems():
            if not trait.output:
                output += "{0}: {1}\n".format(trait_name,
                                            trait_ids(self.trait(trait_name)))
        return output

    def get_inputs(self):
        """ Pipeline inputs

        Returns
        -------
        outputs: dict
            a dictionary with all the input Plugs' names and values
        """
        output = {}
        for trait_name, trait in self.user_traits().iteritems():
            if not trait.output:
                output[trait_name] = getattr(self, trait_name)
        return output

    def get_outputs(self):
        """ Pipeline outputs

        Returns
        -------
        outputs: dict
            a dictionary with all the output Plugs' names and values
        """
        output = {}
        for trait_name, trait in self.user_traits().iteritems():
            if trait.output:
                output[trait_name] = getattr(self, trait_name)
        return output

    def set_qc(self, name, qc_id, **kwargs):
        """ Create and set a viewer.
        """
        self.qc_processes[name] = (qc_id, kwargs)

    def get_qc(self, name):
        """ Get the viewer identified by name
        """
        return self.qc_processes[name]

    def set_viewer(self, name, viewer_id, **kwargs):
        """ Create and set a viewer.
        """
        self.viewers[name] = (viewer_id, kwargs)

    def get_viewer(self, name):
        """ Get the viewer identified by name
        """
        return self.viewers[name]

    def set_parameter(self, name, value):
        """ Set the parameter name of the process
        instance.
        """
        setattr(self, name, value)

    def get_parameter(self, name):
        """ Get the parameter name of the process
        instance.
        """
        return getattr(self, name)

    def _get_log(self, exec_info):
        """ Get process execution information
        """
        log = exec_info.runtime
        log["process"] = self.id
        log["inputs"] = exec_info.inputs.copy()
        log["outputs"] = exec_info.outputs.copy()
        #del log["outputs"]["exec_info"]

        # Need to take the representation of undefined input or outputs
        # traits
        for parameter_type in ["inputs", "outputs"]:
            for key, value in log[parameter_type].iteritems():
                if isinstance(value, _Undefined):
                    log[parameter_type][key] = repr(value)

        return log

    def save_log(self):
        """ Save the Process meta information in json format
        """
        if not self.log_file:
            self.log_file = os.path.join(self.exec_info["cwd"],
                                         "log.json")

        json_struct = unicode(json.dumps(self.exec_info, sort_keys=True,
                                         check_circular=True, indent=4))
        if self.log_file:
            f = open(self.log_file, 'w')
            print >> f, json_struct
            f.close()

    run = LateBindingProperty(_run_process, None, None,
                             "Processing function that has to be defined")


class NipypeProcess(Process):
    """ Dummy class for interfaces.
    """
    def __init__(self, nipype_instance, *args, **kwargs):
        """ Init the nipype process class.
        """
        # Inheritance
        super(NipypeProcess, self).__init__(*args, **kwargs)

        # Some interface identification parameters
        self._nipype_interface = nipype_instance
        self._nipype_module = nipype_instance.__class__.__module__
        self._nipype_class = nipype_instance.__class__.__name__
        self._nipype_interface_name = self._nipype_module.split(".")[2]

        # reset the process name and id
        self.id = ".".join([self._nipype_module, self._nipype_class])
        self.name = self._nipype_interface.__class__.__name__

    def _run_process(self):
        return self._nipype_interface.run()

    run = property(_run_process)


class ProcessResult(object):
    """Object that contains the results of running a particular Process.

    Parameters
    ----------
    process : class type (mandatory)
        A copy of the `Process` class that was call to generate the result.
    runtime : dict (mandatory)
        Execution attributes.
    inputs :  dict (optional)
        Representation of the process inputs.
    outputs : dict (optional)
        Representation of the process outputs.
    """

    def __init__(self, process, runtime, inputs=None, outputs=None):
        self.process = process
        self.runtime = runtime
        self.inputs = inputs
        self.outputs = outputs