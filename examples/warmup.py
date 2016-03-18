"""
This example will warmup your Anova when run.
"""
from pycirculate.anova import AnovaController
import datetime


# Set the temp to 130.0F.
TEMP = 130.0

# Can be found with `sudo hcitool lescan`
ANOVA_MAC_ADDRESS = "78:A5:04:38:B3:FA"

def main():
    ctrl = AnovaController(ANOVA_MAC_ADDRESS)
    print datetime.datetime.now()
    print ctrl.read_temp(), ctrl.read_unit()
    print ctrl.set_temp(TEMP)
    print ctrl.start_anova()
    print ctrl.anova_status()


if __name__ == "__main__":
    main()

