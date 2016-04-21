# -*- coding: utf-8 -*-

#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL-B license under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL-B license as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-B license and that you accept its terms.

'''
Some useful functions to manage file or directorie names.

* author: Yann Cointepas
* organization: `NeuroSpin <http://www.neurospin.org>`_
* license: `CeCILL B <http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html>`_
'''
__docformat__ = "restructuredtext en"

import os
import platform
import fnmatch
import hashlib
import re
import six


def split_path(path):
    '''
    Iteratively apply C{os.path.split} to build a list. Ignore trailing directory separator.

    Examples::
      split_path( '/home/myaccount/data/file.csv' ) returns [ '/', 'home', 'myaccount', 'data', 'file.csv' ]
      split_path( 'home/myaccount/data/file.csv' ) returns [ 'home', 'myaccount', 'data', 'file.csv' ]
      split_path( '/home/myaccount/data/' ) returns [ '/', 'home', 'myaccount', 'data' ]
      split_path( '/home/myaccount/data' ) returns [ '/', 'home', 'myaccount', 'data' ]
      split_path( '' ) returns [ '' ]
  '''
    result = []
    a, b = os.path.split(path)
    if not b:
        a, b = os.path.split(a)
    while a and b:
        result.insert(0, b)
        a, b = os.path.split(a)
    if a:
        result.insert(0, a)
    else:
        result.insert(0, b)
    return result


def relative_path(path, referenceDirectory):
    '''
    Return a relative version of a path given a
    reference directory.

    os.path.join( referenceDirectory, relative_path( path, referenceDirectory ) )
    returns os.path.abspath( path )

    Example
    =======
      relative_path( '/usr/local/brainvisa-3.1/bin/brainvisa', '/usr/local' )
      returns 'brainvisa-3.1/bin/brainvisa'

      relative_path( '/usr/local/brainvisa-3.1/bin/brainvisa', '/usr/local/bin' )
      returns '../brainvisa-3.1/bin/brainvisa'

      relative_path( '/usr/local/brainvisa-3.1/bin/brainvisa', '/tmp/test/brainvisa' )
      returns '../../../usr/local/brainvisa-3.1/bin/brainvisa'
    '''
    sPath = split_path(os.path.abspath(path))
    sReferencePath = split_path(os.path.abspath(referenceDirectory))
    i = 0
    while i < len(sPath) and i < len(sReferencePath) and sPath[i] == sReferencePath[i]:
        i += 1
    plist = (['..'] * (len(sReferencePath) - i)) + sPath[i:]
    if len(plist) == 0:
        return ''
    return os.path.join(*plist)


query_string_re = re.compile( '\?([^\?\&]+\=[^\&]*)(\&[^\?\&]+\=[^\&]*)*$' )

def split_query_string(path):
  '''
  Split a path and its query string.
  
  Example
  =======
  A path containing a query string is :
  /dir1/file1?param1=val1&param2=val2&paramN=valN
  
  split_query_string( '/dir1/file1?param1=val1&param2=val2&paramN=valN' ) would
  return ( '/dir1/file1', '?param1=val1&param2=val2&paramN=valN' )
  
  '''
  m = query_string_re.search(path)
  if m is not None:
    return (path[0:m.start()], path[m.start():] )
    
  else:
    return (path, '')


def remove_query_string(path):
  '''
  Remove the query string from a path.
  
  Example
  =======
  A path containing a query string is :
  /dir1/file1?param1=val1&param2=val2&paramN=valN
  
  remove_query_string( '/dir1/file1?param1=val1&param2=val2&paramN=valN' ) would
  return '/dir1/file1'
  
  '''
  return query_string_re.sub( '', path )

class QueryStringParamUpdateMode:
    REPLACE = 0
    APPEND = 1
    
def update_query_string(
    path, 
    params, 
    params_update_mode = QueryStringParamUpdateMode.REPLACE
):
  '''
  Update the query string parameters in a path.

  :param string path:
        The path to update parameters within.

  :param dict params:
        A dictionnary that contains keys and parameters to set in the query 
        string

  :param (dict|string|list|int) params_update_mode:
        The default value is QueryStringParamUpdateMode.REPLACE that lead to
        replace value in the query string path by the one given in the params
        dictionary.
        It is possible to change the default behaviour giving the value 
        QueryStringParamUpdateMode.APPEND. This will lead to always append
        values of the params dictionary to values of the query string path.
        The default behaviour can also be changed by specifying a parameter name
        as string, in this case only values for that parameter name will be 
        appended. It can also contains a list or a tuple of parameter names for
        which values will be appended.
        Finally, this parameter can be a dictionary that specifies which 
        parameter has to be appended or replaced. The dictionary contains 
        parameter names in its keys and QueryStringParamUpdateMode in values.
        
  :returns:
        The path updated with given parameters
        
  Example
  =======
  A path containing a query string is:
  /dir1/file1?param1=val1&param2=val2&paramN=valN
  
  the params dictionary contains:
  {'param1':'newval1', param2=newval2', param3':'newval3'}
  
  update_query_string('/dir1/file1?param1=val1&param2=val2&paramN=valN',
                      {'param1':'newval1', 'param2':'newval2', 'param3':'newval3'})
  would return:
  '/dir1/file1?param1=newval1&param2=newval2&paramN=valN&param3=newval3'
  
  
  update_query_string('/dir1/file1?param1=val1&param2=val2&paramN=valN',
                      {'param1':'newval1', 'param2':'newval2', 'param3':'newval3'},
                      QueryStringParamUpdateMode.APPEND)
  would return:
  '/dir1/file1?param1=val1&param1=newval1&param2=val2&param2=newval2&paramN=valN&param3=newval3'


  update_query_string('/dir1/file1?param1=val1&param2=val2&paramN=valN',
                      {'param1':'newval1', 'param2':'newval2', 'param3':'newval3'},
                      'param2')
  would return:
  '/dir1/file1?param1=newval1&param2=val2&param2=newval2&paramN=valN&param3=newval3'


  update_query_string('/dir1/file1?param1=val1&param2=val2&paramN=valN',
                      {'param1':'newval1', 'param2':'newval2', 'param3':'newval3'},
                      ('param1', 'param2'))
  would return:
  '/dir1/file1?param1=val1&param1=newval1&param2=val2&param2=newval2&paramN=valN&param3=newval3'

  
  update_query_string('/dir1/file1?param1=val1&param2=val2&paramN=valN',
                      {'param1':'newval1', 'param2':'newval2', 'param3':'newval3'},
                      {'param1': QueryStringParamUpdateMode.APPEND, 
                       'param2': QueryStringParamUpdateMode.REPLACE})
  would return:
  '/dir1/file1?param1=val1&param1=newval1&param2=val2&param2=newval2&paramN=valN&param3=newval3'  
  '''
  import urlparse
  import urllib
  import types
  
  # Convert params_update_mode to a dictionary that contains the update mode
  # for each parameter
  if type(params_update_mode) in (types.ListType, types.TupleType):
    # Update mode is specified using a list of parameter names 
    default_update_mode = QueryStringParamUpdateMode.REPLACE
    params_update = params_update_mode
    params_update_mode = dict()
    
    for p in params_update:
      if (type(p) in (types.ListType, types.TupleType)):
        if (len(p) > 1):
          params_update_mode[p[0]] = p[1]
        elif(len(p) > 0):
          params_update_mode[p[0]] = QueryStringParamUpdateMode.APPEND
      else:
        params_update_mode[p] = QueryStringParamUpdateMode.APPEND
        
  elif type(params_update_mode) in (types.StringType, types.UnicodeType):
    # A parameter name was given directly
    default_update_mode = QueryStringParamUpdateMode.REPLACE
    params_update_mode = dict(((params_update_mode, 
                                QueryStringParamUpdateMode.APPEND),))
    
  elif params_update_mode in (QueryStringParamUpdateMode.APPEND, 
                              QueryStringParamUpdateMode.REPLACE):
    # Update mode was specified for all parameters
    default_update_mode = params_update_mode
    params_update_mode = dict()
      
  elif type(params_update_mode) is types.DictionaryType:
    default_update_mode = QueryStringParamUpdateMode.REPLACE

  else:
    raise RuntimeError('params_update_mode is not specified correctly. '
                       'It must be either a dictionary that contains parameter '
                       'names and the corresponding QueryStringParamUpdateMode, '
                       'either a list that contains parameter names, either'
                       'QueryStringParamUpdateMode.')
     
  url_parsed = urlparse.urlparse(path)
  url_params = urlparse.parse_qs(url_parsed.query)

  # Update parameters dictionary
  for p, v in six.iteritems(params):
    update_mode = params_update_mode.get(
      p,
      default_update_mode
    )
    
    if update_mode == QueryStringParamUpdateMode.REPLACE:
      url_params[p] = v
      
    elif update_mode == QueryStringParamUpdateMode.APPEND:
      if type(v) in (types.ListType, types.TupleType):
        if type(v) is types.TupleType:
          url_params[p] += list(v)
        else:
          url_params[p] += v
          
      else:
        url_params.setdefault(p, list()).append(v)
        
    else:
      raise RuntimeError('params_update_mode is not specified correctly. %s is '
                         'not a valid value for parameter %s. Valid values are '
                         'either QueryStringParamUpdateMode.APPEND, either'
                         'QueryStringParamUpdateMode.REPLACE.' % (v, p))
  url_new = list(url_parsed)
  url_new[4] = urllib.urlencode(url_params, doseq=True)
  
  return urlparse.urlunparse(url_new)

def no_symlink(path):
    '''
    Read all symlinks in path to return the "real" path.

    Example
    =======
      With the following configuration::
        /usr/local/software-1.0 is a directory
        /usr/local/software-1.0/bin is a directory
        /usr/local/software-1.0/bin/command is a file
        /usr/local/software is a symlink to software-1.0
        /home/bin/command is a symlink to /usr/local/software/bin/command
      no_symlink( '/home/bin/command' ) would return '/usr/local/software-1.0/bin/command'

    '''
    s = split_path(p)
    p = ''
    while s:
        p = os.path.join(p, s.pop(0))
        while os.path.islink(p):
            d, f = os.path.split(p)
            p = os.path.normpath(os.path.join(d, os.readlink(p)))
    return p


#: Character used to separate directories in environment variables such as PATH
path_separator = os.pathsep


def find_in_path(file, path=None):
    '''
    Look for a file in a series of directories. By default, directories are
    contained in C{PATH} environment variable. But another environment variable
    name or a sequence of directories names can be given in C{path} parameter.

    Examples::
      find_in_path( 'sh' ) could return '/bin/sh'
      find_in_path( 'libpython2.5.so', 'LD_LIBRARY_PATH' ) could return '/usr/local/lib/libpython2.5.so'
    '''
    if path is None:
        path = os.environ.get('PATH').split(path_separator)
    elif isinstance(path, basestring):
        var = os.environ.get(path)
        if var is None:
            var = path
        path = var.split(path_separator)
    for i in path:
        p = os.path.normpath(os.path.abspath(i))
        if p:
            r = os.path.join(p, file)
            if os.path.isdir(p) and os.path.exists(r):
                return r


def locate_file(pattern, root=os.curdir):
    """
    Locates a file in a directory tree

    :param string pattern:
        The pattern to find

    :param string root:
        The search root directory

    :returns:
        The first found occurrence
    """
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            return os.path.join(path, filename)


def which(program):
    """
    Identifies the location of an executable

    :param string program
        The executable to find

    :returns:
        The full path of the executable
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def update_hash_from_directory(directory, hash):
    '''
    Update a hash object from the content of a directory. The hash will
    reflect the recursive content of all files as well as the paths in all
    directories.
    '''
    for root, dirs, files in sorted(os.walk(directory)):
        for file in sorted(files):
            hash.update(file)
            hash.update(open(os.path.join(root, file)).read())
        for dir in sorted(dirs):
            hash.update(dir)
            update_hash_from_directory(os.path.join(root, dir), hash)


def path_hash(path, hash=None):
    '''
    Return a hash hexdigest for a file or a directory.
    '''
    if hash is None:
        hash = hashlib.md5()
    if os.path.isdir(path):
        update_hash_from_directory(path, hash)
    else:
        hash.update(open(path).read())
    return hash.hexdigest()


def ensure_is_dir(d, clear_dir=False):
    """ If the directory doesn't exist, use os.makedirs """
    if not os.path.exists(d):
        os.makedirs(d)
    elif clear_dir:
        shutil.rmtree(d)
        os.makedirs(d)
