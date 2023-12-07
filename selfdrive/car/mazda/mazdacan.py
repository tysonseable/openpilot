from openpilot.selfdrive.car.mazda.values import GEN1, Buttons

from selfdrive.car.mazda.values import GEN1, GEN2, Buttons
from common.params import Params
import copy

def create_steering_control(packer, car_fingerprint, frame, apply_steer, lkas):

  if car_fingerprint in GEN1:
    tmp = apply_steer + 2048

    lo = tmp & 0xFF
    hi = tmp >> 8

    # copy values from camera
    b1 = int(lkas["BIT_1"])
    er1 = int(lkas["ERR_BIT_1"])
    lnv = 0
    ldw = 0
    er2 = int(lkas["ERR_BIT_2"])

    # Some older models do have these, newer models don't.
    # Either way, they all work just fine if set to zero.
    steering_angle = 0
    b2 = 0

    tmp = steering_angle + 2048
    ahi = tmp >> 10
    amd = (tmp & 0x3FF) >> 2
    amd = (amd >> 4) | (( amd & 0xF) << 4)
    alo = (tmp & 0x3) << 2

    ctr = frame % 16
    # bytes:     [    1  ] [ 2 ] [             3               ]  [           4         ]
    csum = 249 - ctr - hi - lo - (lnv << 3) - er1 - (ldw << 7) - ( er2 << 4) - (b1 << 5)

    # bytes      [ 5 ] [ 6 ] [    7   ]
    csum = csum - ahi - amd - alo - b2

    if ahi == 1:
      csum = csum + 15

    if csum < 0:
      if csum < -256:
        csum = csum + 512
      else:
        csum = csum + 256

    csum = csum % 256
    
    bus = 0
    sig_name = "CAM_LKAS"

    values = {
      "LKAS_REQUEST": apply_steer,
      "CTR": ctr,
      "ERR_BIT_1": er1,
      "LINE_NOT_VISIBLE" : lnv,
      "LDW": ldw,
      "BIT_1": b1,
      "ERR_BIT_2": er2,
      "STEERING_ANGLE": steering_angle,
      "ANGLE_ENABLED": b2,
      "CHKSUM": csum
    }
      
  elif car_fingerprint in GEN2:
    bus = 1
    sig_name = "EPS_LKAS"
    values = {
      "LKAS_REQUEST": apply_steer,
      "STEER_FEEL": 12000,
    }

  return packer.make_can_msg(sig_name, bus, values)

def create_ti_steering_control(packer, car_fingerprint, frame, apply_steer):

  key = 3294744160
  chksum = apply_steer

  if car_fingerprint in GEN1:
    values = {
        "LKAS_REQUEST"     : apply_steer,
        "CHKSUM"           : chksum,
        "KEY"              : key
     }
  # TODO
  # 1. Add new CAR values for MDARS Mazdas so that we can change the rate of the message. This will take some work.
  # 2. Listen for reply's on both CAN buses if not MDARS version of
  # Mazda (2021+ or m3 2019+) and warn the user if there is a bad connection
  # but do not cause disengagment

  # Write to both buses for *future* redundancy, but we only check bus 1 for a response in carstate and safey_mazda.h for now.
  # if (frame % 2 == 0):
  #  commands.append(packer.make_can_msg("CAM_LKAS2", 0, values))

  return packer.make_can_msg("CAM_LKAS2", 1, values)



def create_alert_command(packer, cam_msg: dict, ldw: bool, steer_required: bool):
  values = {s: cam_msg[s] for s in [
    "LINE_VISIBLE",
    "LINE_NOT_VISIBLE",
    "LANE_LINES",
    "BIT1",
    "BIT2",
    "BIT3",
    "NO_ERR_BIT",
    "S1",
    "S1_HBEAM",
  ]}
  values.update({
    # TODO: what's the difference between all these? do we need to send all?
    "HANDS_WARN_3_BITS": 0b111 if steer_required else 0,
    "HANDS_ON_STEER_WARN": steer_required,
    "HANDS_ON_STEER_WARN_2": steer_required,

    # TODO: right lane works, left doesn't
    # TODO: need to do something about L/R
    "LDW_WARN_LL": 0,
    "LDW_WARN_RL": 0,
  })
  return packer.make_can_msg("CAM_LANEINFO", 0, values)


def create_button_cmd(packer, car_fingerprint, counter, button):

  can = int(button == Buttons.CANCEL)
  res = int(button == Buttons.RESUME)

  if car_fingerprint in GEN1:
    values = {
      "CAN_OFF": can,
      "CAN_OFF_INV": (can + 1) % 2,

      "SET_P": 0,
      "SET_P_INV": 1,

      "RES": res,
      "RES_INV": (res + 1) % 2,

      "SET_M": 0,
      "SET_M_INV": 1,

      "DISTANCE_LESS": 0,
      "DISTANCE_LESS_INV": 1,

      "DISTANCE_MORE": 0,
      "DISTANCE_MORE_INV": 1,

      "MODE_X": 0,
      "MODE_X_INV": 1,

      "MODE_Y": 0,
      "MODE_Y_INV": 1,

      "BIT1": 1,
      "BIT2": 1,
      "BIT3": 1,
      "CTR": (counter + 1) % 16,
    }

    return packer.make_can_msg("CRZ_BTNS", 0, values)
  
def create_acc_cmd(self, packer, CS, CC, hold, resume):
  if self.CP.carFingerprint in GEN2:
    values = CS.acc
    msg_name = "ACC"
    bus = 2

    if (values["ACC_ENABLED"]):
      if Params().get_bool("ExperimentalLongitudinalEnabled"):
        values["ACCEL_CMD"] = (CC.actuators.accel * 240) + 2000
      values["HOLD"] = hold
      values["RESUME"] = resume
    else:
      pass

  return packer.make_can_msg(msg_name, bus, values)

OBFUSCATION_MASKS = [ 
         24,
         194,
         131,
         89,
         1,
         219,
         154,
         64,
         42,
         240,
         177,
         107,
         51,
         233,
         168,
         114
        ]

def compute_7bit_checksum(value):
    # Assuming 'value' is a 14-bit integer
    # Masking with 0b1111111 (which is 127 in decimal) to get the lower 7 bits
    lower_7_bits = value & 0b1111111

    # Shifting right by 7 bits and then masking to get the upper 7 bits
    upper_7_bits = (value >> 7) & 0b1111111

    # Summing the two parts
    sum_of_bits = lower_7_bits + upper_7_bits

    # Applying modulo 128 to ensure the result is a 7-bit number
    checksum = sum_of_bits % 128

    return checksum

def create_lkas_2019(packer, CS, self, frame):
  values = CS.lkas
  new_values = copy.copy(values)
  ctr = int(values["4_BIT_COUNTER"])
  msg_name = "LKAS_"
  bus = 2
  a = compute_7bit_checksum(int(values["STEER"])) * 2
  a = a%63
  values["CHECK"] = a

  values["MASKED_BYTE"] = int(values["MASKED_BYTE"]) ^ OBFUSCATION_MASKS[ctr] & 0xFF
  #values["MASKED_BYTE"] = int(OBFUSCATION_MASKS[ctr])
  return packer.make_can_msg(msg_name, bus, values)

#signal = 8190 check = 60 dif = /0
#signal = 8191 check = 63 dif = /3
#signal = 8192 check = 0  dif = /1
#signal = 8193 check = 2  dif = /2
#signal = 8194 check = 4  dif = /2
#signal = 8195 check = 33 dif = /0
#signal = 8196 check = 10 check_difference = 0
#signal = 8197 check = 12 check_difference = 2
#signal = 8198 check = 15 check_difference = 3
#signal = 8199 check = 18 check_difference = 3
#signal = 8200 check = 20 check_difference = 2
#signal = 8201 check = 23 check_difference = 3
#signal = 8202 check = 26 check_difference = 3
#signal = 8203 check = 28 check_difference = 2
#signal = 8204 check = 31 check_difference = 3
#signal = 8205 check = 34 check_difference = 3
#signal = 8206 check = 36 check_difference = 2
#signal = 8207 check = 39 check_difference = 3
#signal = 8208 check = 42 check_difference = 3
#signal = 8209 check = 44 check_difference = 2
#signal = 8210 check = 47 check_difference = 3
#signal = 8211 check = 50 check_difference = 3
#signal = 8212 check = 52 check_difference = 2

def create_lkas2_2019(packer, CS, CC, frame):
  values = CS.lkas
  ctr = int(values["4_BIT_COUNTER"])
  msg_name = "LKAS_"
  bus = 0
  
  return packer.make_can_msg(msg_name, bus, values)