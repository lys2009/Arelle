'''
Created on Oct 3, 2010

@author: Mark V Systems Limited
(c) Copyright 2010 Mark V Systems Limited, All rights reserved.
'''
import gc, sys, traceback
from arelle import (ModelXbrl, Validate, DisclosureSystem)

def initialize(cntlr):
    modelManager = ModelManager(cntlr)
    modelManager.modelXbrl = None
    return modelManager
    

class ModelManager:
    
    def __init__(self, cntlr):
        self.cntlr = cntlr
        self.validateDisclosureSystem = False
        self.disclosureSystem = DisclosureSystem.DisclosureSystem(self)
        self.validateCalcLB = False
        self.validateInferDecimals = False
        self.validateUtr = False
        self.loadedModelXbrls = []
        from arelle import Locale
        self.locale = Locale.getUserLocale()
        self.defaultLang = Locale.getLanguageCode()

    def shutdown(self):
        self.status = "shutdown"
        
    def addToLog(self, message):
        self.cntlr.addToLog(message)
        
    def showStatus(self, message, clearAfter=None):
        self.cntlr.showStatus(message, clearAfter)
        
    def viewModelObject(self, modelXbrl, objectId):
        self.cntlr.viewModelObject(modelXbrl, objectId)
        
    def reloadViews(self, modelXbrl):
        self.cntlr.reloadViews(modelXbrl)
        
    def load(self, filesource, nextaction=None):
        try:
            if filesource.url.startswith("urn:uuid:"): # request for an open modelXbrl
                for modelXbrl in self.loadedModelXbrls:
                    if not modelXbrl.isClosed and modelXbrl.uuid == filesource.url:
                        return modelXbrl
                raise IOError(_("Open file handle is not open: {0}".format(filesource.url)))
        except AttributeError:
            pass # filesource may be a string, which has no url attribute
        self.filesource = filesource
        self.modelXbrl = ModelXbrl.load(self, filesource, nextaction)
        self.loadedModelXbrls.append(self.modelXbrl)
        return self.modelXbrl
    
    def saveDTSpackage(self, allDTSes=False):
        if allDTSes:
            for modelXbrl in self.loadedModelXbrls:
                modelXbrl.saveDTSpackage()
        elif self.modelXbrl is not None:
            self.modelXbrl.saveDTSpackage()
    
    def create(self, newDocumentType=None, url=None, schemaRefs=None, createModelDocument=True):
        self.modelXbrl = ModelXbrl.create(self, newDocumentType, url, schemaRefs, createModelDocument)
        self.loadedModelXbrls.append(self.modelXbrl)
        return self.modelXbrl
    
    def validate(self):
        try:
            if self.modelXbrl:
                Validate.validate(self.modelXbrl)
        except Exception as err:
            self.addToLog(_("[exception] Validation exception: {0} at {1}").format(
                           err,
                           traceback.format_tb(sys.exc_info()[2])))
        
    def compareDTSes(self, versReportFile, writeReportFile=True):
        from arelle.ModelVersReport import ModelVersReport
        if len(self.loadedModelXbrls) >= 2:
            fromDTS = self.loadedModelXbrls[-2]
            toDTS = self.loadedModelXbrls[-1]
            from arelle.ModelDocument import Type
            modelVersReport = self.create(newDocumentType=Type.VERSIONINGREPORT,
                                          url=versReportFile,
                                          createModelDocument=False)
            ModelVersReport(modelVersReport).diffDTSes(versReportFile, fromDTS, toDTS)
            return modelVersReport
        return None
        
    def close(self, modelXbrl=None):
        if modelXbrl is None: modelXbrl = self.modelXbrl
        if modelXbrl:
            while modelXbrl in self.loadedModelXbrls:
                self.loadedModelXbrls.remove(modelXbrl)
            if (modelXbrl == self.modelXbrl): # dereference modelXbrl from this instance
                if len(self.loadedModelXbrls) > 0:
                    self.modelXbrl = self.loadedModelXbrls[0]
                else:
                    self.modelXbrl = None
            modelXbrl.close()
            gc.collect()

