from PySide import QtCore


class PushButtonWrapper(QtCore.QObject):
    """
        Gui class, which maps a ParamPushButton.
    """

    def __init__(self, param):
        QtCore.QObject.__init__(self)
        self._param = param
        self._param.changed.connect(self.emitChanged)

    #################### getters ####################

    def getParamType(self):
        return self._param.getParamType()
    
    def getLabel(self):
        return self._param.setLabel()

    def getTrigger(self):
        return self._param.setTrigger()

    def getEnabled(self):
        return self._param.setEnabled()

    #################### setters ####################

    def setParamType(self, paramType):
        self._param.setParamType(paramType)

    def setLabel(self, label):
        self._param.setLabel(label)

    def setTrigger(self, trigger):
        self._param.setTrigger(trigger)

    def setEnabled(self, enabled):
        self._param.setEnabled(enabled)

    @QtCore.Signal
    def changed(self):
        pass

    def emitChanged(self):
        self.changed.emit()

    ################################################## DATA EXPOSED TO QML ##################################################

    paramType = QtCore.Property(unicode, getParamType, setParamType, notify=changed)
    label = QtCore.Property(str, getLabel, setLabel, notify=changed)
    trigger = QtCore.Property(str, getTrigger, setTrigger, notify=changed)
    enabled = QtCore.Property(bool, getEnabled, setEnabled, notify=changed)
