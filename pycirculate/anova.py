from bluepy import btle
import datetime

class AnovaDelegate(btle.DefaultDelegate):
    """
    Process notifications from Anova.
    """
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

        self.last_notifications = []

    def handleNotification(self, cHandle, data):
        # print repr(self), "handleNotification(), cHandle: ", cHandle, "data: ",  data
        self._store_notification(cHandle, data)

    def _store_notification(self, cHandle, data):
        self.last_notifications.append((cHandle, data))
        # keep the last 10 notifications
        self.last_notifications = self.last_notifications[-10:]

    def get_last_notification(self):
        return self.last_notifications[-1]


class AnovaController(object):
    def __init__(self, mac_address, connect=True):
        self.MAC_ADDRESS = mac_address
        self.is_connected = False
        if connect:
            self.connect()

    def connect(self):
        self.anova = btle.Peripheral(self.MAC_ADDRESS)
        self.anova.setDelegate(AnovaDelegate())
        # Service UUID:        0xFFE0
        services = self.anova.getServices()
        self.service = self.anova.getServiceByUUID("FFE0")
        # Characteristic UUID: 0xFFE1
        self.characteristic = self.service.getCharacteristics()[0]
        self.is_connected = True

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        try:
            self.anova.disconnect()
        except AttributeError:
            # probably had a problem connecting in the first place.
            pass
        self.is_connected = False

    def _send_command(self, command):
        command = "{0}\r".format(command)
        self.characteristic.write(command)

    def _read(self):
        #self.characteristic.read()
        if self.anova.waitForNotifications(1.0):
            # looks like we got out notifcation!
            # maybe we should pass a reference to self into the Delegate through a callback...
            return self.anova.delegate.get_last_notification()

    def send_command_async(self, command):
        self._send_command(command)
        _, output = self._read()
        return output.strip()

    ##### Temperature commands

    def read_unit(self):
        """
        Returns the current temperature unit as 'c' or 'f' for Celcius and Farenheit respectively.
        """
        return self.send_command_async("read unit")

    def set_unit(self, unit):
        """
        Set the current temperature unit to Celcius or Farenheit. Returns either 'c' or 'f' depending on the unit being set.
        """
        assert unit in ['c', 'f'], "Valid temperature units are 'c' and 'f'."
        return self.send_command_async("set unit {}".format(unit))

    def read_temp(self):
        """
        Returns the current temperature as a floating point number. This value will be in the temperature units set on the device.
        """
        return self.send_command_async("read temp")

    def read_set_temp(self):
        """
        Returns the target temperature as a floating point number. This value will be in the temperature units set on the device.
        """
        return self.send_command_async("read set temp")

    def set_temp(self, degrees):
        """
        Returns the target temperature as a floating point number. This value will be in the temperature units set on the device.
        """
        return self.send_command_async("set temp {}".format(degrees))

    def read_calibration_factor(self):
        """
        Returns the current temperature calibration factor of the device. The original value is 0.0. 
        It is temperature displayed by device minus temperature measured by device in Celsius.
        """
        return self.send_command_async("read cal")

    def set_calibration_factor(self, factor):
        """
        Set the current temperature calibration factor of the device. Accepted values range is -9.9 to 9.9. 
        (This is Celsius, no matter what is current unit.) Echoes the executed command.
        """
        assert factor >= -9.9 and factor <= 9.9, "Invalid factor"
        return self.send_command_async("set temp {}".format(factor))

    def read_temperature_history(self):
        """
        Returns all the available temperature history data. This returns a list of entries, each entry 
        containing a temperature date and time. The form is each entry is 'temp MM DD hh mm'. 
        The temperature will be in the current units set on the device.
        """
        return self.send_command_async("read data")

    ##### Device operation commands

    def anova_status(self):
        """
        Returns the current operational status of the device. 
        The potential return values are 'running', 'stopped', 'low water', 'heater error', 
        or 'power interrupt error'. Haven't validated that the last two are correct yet.
        """
        return self.send_command_async("status")

    def start_anova(self):
        """
        Start the device. Seems to always return 'start' even if the device doesn't start.
        """
        return self.send_command_async("start")

    def stop_anova(self):
        """
        Stop the device. Seems to always return 'stop'.
        """
        return self.send_command_async("stop")

    ##### Timer commands

    def read_timer(self):
        """
        Read the number of minutes on the timer and whether or not it's running. The return value is of the form 'running|stopped'
        """
        return self.send_command_async("read timer")

    def set_timer(self, minutes):
        """
        Set the number of minutes on the timer. Returns the value that is set.
        """
        return self.send_command_async("set timer {}".format(minutes))

    def start_timer(self):
        """
        Starts the timer. Return value is the echoed command. Note that device must already be started to start the timer.
        """
        return self.send_command_async("start time")

    def stop_timer(self):
        """
        Stops the timer. Return value is the echoed command. Note that stopping the device also automatically stops the timer.
        """
        return self.send_command_async("stop time")

    ##### Program commands

    def read_program_status(self):
        """
        Returns the current program that is set. The return value is of the form 'program' followed by the individual time-minutes pairs.
        """
        return self.send_command_async("program status")

    def set_program(self, *temp_minute_pairs):
        """
        Set a multistep programe on the device. Seems like these need to be set in temperature and number 
        of minutes pairs. Appears to be a max of 6 steps and any after that are ignored.
        
        Pass in up to 6 tuples of (temperature, minute) pairs.
        """
        assert len(temp_minute_pairs) <= 6, "The Anova ignores programs longer than 6 steps."
        program = " ".join("{0} {1}".format(t, m) for t,m in temp_minute_pairs)
        return self.send_command_async("set program {}".format(program))

    def start_program(self):
        """
        Start the current program. Returns the echoed command. Needs more testing.
        """
        return self.send_command_async("start program")
    
    def stop_program(self):
        """
        Stop the current program. Returns the echoed command. Needs more testing.
        """
        return self.send_command_async("stop program")

    def resume_program(self):
        """
        Resume the current program. Returns the echoed command. Needs more testing.
        """
        return self.send_command_async("resume program")


    ##### System commands

    def set_led(self, red, green, blue):
        """
        Change the mouse wheel color on the device. The RGB values are integers from 0-255. 
        The return value is the echoed command if successful.
        """
        for color, rgb in [("red", red), ("green", green), ("blue", blue),]:
            assert rgb >= 0 and rgb <= 255, "{0}'s RGB value must be an integer from 0-255".format(color)
        return self.send_command_async("set led {red} {green} {blue}".format(red=red, green=green, blue=blue))

    def set_bluetooth_name(self, name):
        """
        Set the Bluetooth display name of the device. This will cause the device to disconnect.
        """
        return self.send_command_async("set name {}".format(name))

    def read_date(self):
        """"
        Supposedly reads the date and time set on the device. The return value is of the form 'YY MM DD hh mm' with 
        two digit values of year, month, day of month, hour and minute respectively. I also noticed that 
        the clock didn't seem to run on the device until after calling 'set date' for the first time. 
        Before that it was always returning the origal time value (same for the 'read data' entries).
        """
        return self.send_command_async("read date")

    def set_date(self, date=None):
        """
        Set the current date and time on the device. Note that this is a 24 hour clock.
        """
        if not date:
            date = datetime.datetime.now()
        command = "set date {}".format(date.strftime("%y %m %d %H %M"))
        return self.send_command_async(command)



        
