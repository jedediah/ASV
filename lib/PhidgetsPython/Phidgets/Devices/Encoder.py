"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.6'
__date__ = 'April 9 2009'

from threading import *
from ctypes import *
from Phidgets.Phidget import *
from Phidgets.PhidgetException import *
import sys

class Encoder(Phidget):
    """This class represents a Phidget Encoder. All methods to read encoder data from an encoder are implemented in this class.
    
    Phidget Encoder boards generally support 1 or more encoders with 0 or more digital inputs. Both high speed optical and low speed mechanical encoders are supported with this API.
    
    Extends:
        Phidget
    """
    def __init__(self):
        """The Constructor Method for the Encoder Class
        """
        Phidget.__init__(self)
        
        self.__inputChange = None
        self.__positionChange = None
        
        self.__onInputChange = None
        self.__onPositionChange = None
        
        PhidgetLibrary.getDll().CPhidgetEncoder_create(byref(self.handle))
        
        if sys.platform == 'win32':
            self.__INPUTCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__POSITIONCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int)
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__INPUTCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__POSITIONCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int)

    def getPosition(self, index):
        """Returns the position of an encoder.
        
        This is an absolute position as calcutated since the encoder was plugged in.
        This value can be reset to anything using setPosition.
        
        Parameters:
            index<int>: index of the encoder.
        
        Returns:
            The position of the encoder <int>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or if the index is out of range.
        """
        position = c_int()
        result = PhidgetLibrary.getDll().CPhidgetEncoder_getPosition(self.handle, c_int(index), byref(position))
        if result > 0:
            raise PhidgetException(result)
        else:
            return position.value

    def setPosition(self, index, position):
        """Sets the position of a specific encoder.
        
        This resets the internal position count for an encoder.
        This call in no way actually sends information to the device, as an absolute position is maintained only in the library.
        After this call, position changes from the encoder will use the new value to calculate absolute position as reported by the change handler.
        
        Parameters:
            index<int>: index of the encoder.
            position<position>: new position for this encoder.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or if the index is out of range.
        """
        result = PhidgetLibrary.getDll().CPhidgetEncoder_setPosition(self.handle, c_int(index), c_int(position))
        if result > 0:
            raise PhidgetException(result)

    def getInputState(self, index):
        """Returns the state of a digital input.
        
        On the mechanical encoder this refers to the pushbutton.
        The high speed encoder does not have any digital inputs. A value of true means that the input is active(the button is pushed).
        
        Parameters:
            index<int>: index of the input.
        
        Returns:
            The state of the input <boolean>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or if the index is out of range.
        """
        inputState = c_int()
        result = PhidgetLibrary.getDll().CPhidgetEncoder_getInputState(self.handle, c_int(index), byref(inputState))
        if result > 0:
            raise PhidgetException(result)
        else:
            if inputState.value ==1:
                return True
            else:
                return False

    def getEncoderCount(self):
        """Returns number of encoders.
        
        All current encoder boards support one encoder.
        
        Returns:
            The number of encoders <int>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        encoderCount = c_int()
        result = PhidgetLibrary.getDll().CPhidgetEncoder_getEncoderCount(self.handle, byref(encoderCount))
        if result > 0:
            raise PhidgetException(result)
        else:
            return encoderCount.value

    def getInputCount(self):
        """Returns number of digital inputs.
        
        On the mechanical encoder this refers to the pushbutton.
        The high speed encoder does not have any digital inputs.
        
        Returns:
            The number of inputs <int>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        inputCount = c_int()
        result = PhidgetLibrary.getDll().CPhidgetEncoder_getInputCount(self.handle, byref(inputCount))
        if result > 0:
            raise PhidgetException(result)
        else:
            return inputCount.value

    def __nativeInputChangeEvent(self, handle, usrptr, index, value):
        if self.__inputChange != None:
            if value == 1:
                state = True
            else:
                state = False
            self.__inputChange(InputChangeEventArgs(index, state))
        return 0

    def setOnInputChangeHandler(self, inputChangeHandler):
        """Sets the input change event handler.
        
        The input change handler is a method that will be called when an input on this Encoder board has changed.
        
        Parameters:
            inputChangeHandler: hook to the inputChangeHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__inputChange = inputChangeHandler
        self.__onInputChange = self.__INPUTCHANGEHANDLER(self.__nativeInputChangeEvent)
        result = PhidgetLibrary.getDll().CPhidgetEncoder_set_OnInputChange_Handler(self.handle, self.__onInputChange, None)
        if result > 0:
            raise PhidgetException(result)

    def __nativePositionChangeEvent(self, handle, usrptr, index, time, position):
        if self.__positionChange != None:
            self.__positionChange(EncoderPositionChangeEventArgs(index, time, position))
        return 0

    def setOnPositionChangeHandler(self, positionChangeHandler):
        """Sets the position change event handler.
        
        The position change handler is a method that will be called when the position of an encoder changes.
        The position change event provides data about how many ticks have occured, and how much time has passed since the last position change event,
        but does not contain an absolute position.
        This can be obtained from getEncoderPosition.
        
        Parameters:
            positionChangeHandler: hook to the positionChangeHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__positionChange = positionChangeHandler
        self.__onPositionChange = self.__POSITIONCHANGEHANDLER(self.__nativePositionChangeEvent)
        result = PhidgetLibrary.getDll().CPhidgetEncoder_set_OnPositionChange_Handler(self.handle, self.__onPositionChange, None)
        if result > 0:
            raise PhidgetException(result)
