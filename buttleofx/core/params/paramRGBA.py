from quickmamba.patterns import Signal


class ParamRGBA(object):
    """
        Core class, which represents a RGBA parameter.
        Contains :
            - _paramType : the name of the type of this parameter
    """

    def __init__(self, tuttleParam):
        self._tuttleParam = tuttleParam

        self.changed = Signal()

    #################### getters ####################

    def getTuttleParam(self):
        return self._tuttleParam

    def getParamType(self):
        return "ParamRGBA"

    def getDefaultR(self):
        return self._tuttleParam.getDoubleValueAtIndex(0)

    def getDefaultG(self):
        return self._tuttleParam.getDoubleValueAtIndex(1)

    def getDefaultB(self):
        return self._tuttleParam.getDoubleValueAtIndex(2)

    def getDefaultA(self):
        print "fguhdgvgjhc", self._tuttleParam.getDoubleValueAtIndex(3)
        return self._tuttleParam.getDoubleValueAtIndex(3)

    def getValue(self):
        return (self.getValueR(), self.getValueG(), self.getValueB(), self.getValueA())

    def getValueR(self):
        return self._tuttleParam.getDoubleValueAtIndex(0)

    def getValueG(self):
        return self._tuttleParam.getDoubleValueAtIndex(1)

    def getValueB(self):
        return self._tuttleParam.getDoubleValueAtIndex(2)

    def getValueA(self):
        return self._tuttleParam.getDoubleValueAtIndex(3)

    def getText(self):
        return self._tuttleParam.getName()[0].capitalize() + self._tuttleParam.getName()[1:]

    #################### setters ####################

    def setValue(self, values):
        self.setValueR(values[0])
        self.setValueG(values[1])
        self.setValueB(values[2])
        self.setValueA(values[3])

    def setValueR(self, value1):
        self._tuttleParam.setValueAtIndex(0, int(value1))
        self.changed()

        print "Rouge : ", self.getValueR()

        from buttleofx.data import ButtleDataSingleton
        buttleData = ButtleDataSingleton().get()
        buttleData.updateMapAndViewer()

    def setValueG(self, value2):
        self._tuttleParam.setValueAtIndex(1, int(value2))
        self.changed()

        print "Vert : ", self.getValueG()
        
        from buttleofx.data import ButtleDataSingleton
        buttleData = ButtleDataSingleton().get()
        buttleData.updateMapAndViewer()

    def setValueB(self, value3):
        self._tuttleParam.setValueAtIndex(2, int(value3))
        self.changed()

        print "Blue : ", self.getValueB()
        
        from buttleofx.data import ButtleDataSingleton
        buttleData = ButtleDataSingleton().get()
        buttleData.updateMapAndViewer()

    def setValueA(self, value4):
        self._tuttleParam.setValueAtIndex(3, 1)
        self.changed()

        print "Alpha : ", self.getValueA()
        
        from buttleofx.data import ButtleDataSingleton
        buttleData = ButtleDataSingleton().get()
        buttleData.updateMapAndViewer()
