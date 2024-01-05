import pump_code_pack
from nesp_lib import Port, Pump, PumpingDirection


def PumpConnect(port, pumpName):
    if pumpName == "PHD":
        pump_port = pump_code_pack.SerialConnection(port)
        address = 0
        pump = pump_code_pack.Pump2000(pump_port, address, name="PHD2000")
    elif pumpName == "NE":
        pump_port = Port(port)
        pump = Pump(pump_port)
    else:
        pump = "null"
        pump_port = "null"
        print("Pump name is wrong. It should be PHD or NE.")
    return pump, pump_port


def PumpClosePort(port, pumpName):
    if pumpName == "PHD":
        port.close()
    elif pumpName == "NE":
        pass


def PumpInit(pump, pumpName, diameter, infusion_rate, num_syringes):
    infusion_rate = infusion_rate / num_syringes
    if pumpName == "PHD":
        pump.set_dia(diameter)  # set syringe diameter
        pump.set_pump_mode()  # set pump to pump mode (infuse indefinitely)
        inf_rate_units = "ml/hr"
        pump.set_infuse_rate(
            infusion_rate, inf_rate_units
        )  # set initial infuse rate with infuse rate units
    elif pumpName == "NE":
        pump.syringe_diameter = diameter
        pump.pumping_direction = PumpingDirection.INFUSE
        pump.pumping_rate = float(infusion_rate / 60)  # Convert to ml/min from ml/hr


def PumpOn(pump, pumpName):
    if pumpName == "PHD":
        pump.set_irun()
    elif pumpName == "NE":
        pump.run(False)


def PumpOff(pump, pumpName):
    if pumpName == "PHD":
        pump.set_stop()
    elif pumpName == "NE":
        pump.stop()


# Reverse at max speed for continuous infusion
def PumpReverse(pump, pumpName, refill_rate, num_syringes):
    refill_rate = refill_rate / num_syringes
    if pumpName == "PHD":
        pump.set_withdraw_rate(refill_rate, "ml/min")
        pump.set_wrun()
    elif pumpName == "NE":
        pump.stop()
        pump.pumping_direction = PumpingDirection.WITHDRAW
        pump.pumping_rate = float(refill_rate)  # ml/min
        pump.run(False)


def PumpForward(pump, pumpName, infusion_rate, num_syringes):
    infusion_rate = infusion_rate / num_syringes
    if pumpName == "PHD":
        pump.set_infuse_rate(infusion_rate, "ml/hr")
        pump.set_irun()
    elif pumpName == "NE":
        pump.stop()
        pump.pumping_direction = PumpingDirection.INFUSE
        pump.pumping_rate = float(infusion_rate / 60)  # Convert to ml/min from ml/hr
        pump.run(False)


def PumpRateSet(pump, pumpName, infusion_rate, num_syringes):
    infusion_rate = infusion_rate / num_syringes
    if pumpName == "PHD":
        pump.set_infuse_rate(infusion_rate, "ml/hr")
    elif pumpName == "NE":
        # NE1000 refuses infusion rate updates while infusing, so we very shortly turn it off and on again to
        # update the infusion rate. The delay caused by this is negligible (milliseconds)
        pump.stop()
        pump.pumping_rate = float(infusion_rate / 60)
        pump.run(False)
