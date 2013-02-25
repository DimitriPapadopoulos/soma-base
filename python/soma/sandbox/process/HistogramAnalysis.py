## -*- coding: utf-8 -*-
#Process HistogramAnalysis

from traits.api import HasTraits,Str, Int, Enum, Float, File, Bool

class HistogramAnalysis(HasTraits):
   
    
    def __init__(self):   
        #Definition des paramètres du process 
        self.use_hfiltered = Bool(True)
        self.use_wridges=Bool(True)
        self.undersampling=Enum(['2', '4', '8', '16', '32', 'auto', 'iteration'])
        
        #Input
        self.mri_corrected=File(exists=True)
        self.hfiltered=File(exists=True)
        self.white_ridges=File(exists=True)
        #Ouput
        self.histo_analysis=File(exists=False)

        
    def run(self,path,input):
        print 'RUN'  
        option_list = []
        constant_list = ['VipHistoAnalysis', '-i', self.mri_corrected.fullPath(), '-o', self.histo_analysis.fullPath(), '-Save', 'y']  
        if self.use_hfiltered and self.hfiltered is not None:
            option_list += ['-Mask', self.hfiltered.fullPath()]
        if self.use_wridges and self.white_ridges is not None:
            option_list += ['-Ridge', self.white_ridges.fullPath()]
        if self.undersampling == 'iteration':
            option_list += ['-mode', 'i']
        else:
            option_list += ['-mode', 'a', '-u', self.undersampling]
        apply( context.system, constant_list+option_list )
    

        # RUN       
        args=['VipHistoAnalysis','-i',self.mri_corrected,\
        '-o',self.histo_analysis,\
        '-Save', 'y',\
            ]
        str_args = [ str(x) for x in args ] 
        subprocess.call(str_args+option_list)      
