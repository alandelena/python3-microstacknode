import sys
import time
from microstackcommon.i2c import I2CMaster, writing_bytes, writing, reading


DEFAULT_I2C_BUS = 1

# CTRL_REG1_XM
TEMP_EN = 0x80

class LSM9DS0RegisterReadOnlyError(Exception):
    pass


class LSM9DS0(I2CMaster):
    """iNEMO inertial module: 3D accelerometer, 3D gyroscope, 3D magnetometer.

        http://www.st.com/web/en/catalog/sense_power/FM89/SC1448/PF258556
        http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/DM00087365.pdf

    """

    XM_I2C_ADDR = 0x1E
    G_I2C_ADDR = 0x6A

    def __init__(self, bus=DEFAULT_I2C_BUS):
        super().__init__(bus)
        self.who_am_i_g = LSM9DS0Register(0x0F, self.G_I2C_ADDR, self, True)
        self.ctrl_reg1_g = LSM9DS0Register(0x20, self.G_I2C_ADDR, self)
        self.ctrl_reg2_g = LSM9DS0Register(0x21, self.G_I2C_ADDR, self)
        self.ctrl_reg3_g = LSM9DS0Register(0x22, self.G_I2C_ADDR, self)
        self.ctrl_reg4_g = LSM9DS0Register(0x23, self.G_I2C_ADDR, self)
        self.ctrl_reg5_g = LSM9DS0Register(0x24, self.G_I2C_ADDR, self)
        self.reference_g = LSM9DS0Register(0x25, self.G_I2C_ADDR, self)
        self.status_reg_g = LSM9DS0Register(0x27, self.G_I2C_ADDR, self, True)
        self.out_x_l_g = LSM9DS0Register(0x28, self.G_I2C_ADDR, self, True)
        self.out_x_h_g = LSM9DS0Register(0x29, self.G_I2C_ADDR, self, True)
        self.out_y_l_g = LSM9DS0Register(0x2A, self.G_I2C_ADDR, self, True)
        self.out_y_h_g = LSM9DS0Register(0x2B, self.G_I2C_ADDR, self, True)
        self.out_z_l_g = LSM9DS0Register(0x2C, self.G_I2C_ADDR, self, True)
        self.out_z_h_g = LSM9DS0Register(0x2D, self.G_I2C_ADDR, self, True)
        self.fifo_ctrl_reg_g = LSM9DS0Register(0x2E, self.G_I2C_ADDR, self)
        self.fifo_src_reg_g = LSM9DS0Register(0x2F, self.G_I2C_ADDR, self, True)
        self.int1_cfg_g = LSM9DS0Register(0x30, self.G_I2C_ADDR, self)
        self.int1_src_g = LSM9DS0Register(0x31, self.G_I2C_ADDR, self, True)
        self.int1_tsh_xh_g = LSM9DS0Register(0x32, self.G_I2C_ADDR, self)
        self.int1_tsh_xl_g = LSM9DS0Register(0x33, self.G_I2C_ADDR, self)
        self.int1_tsh_yh_g = LSM9DS0Register(0x34, self.G_I2C_ADDR, self)
        self.int1_tsh_yl_g = LSM9DS0Register(0x35, self.G_I2C_ADDR, self)
        self.int1_tsh_zh_g = LSM9DS0Register(0x36, self.G_I2C_ADDR, self)
        self.int1_tsh_zl_g = LSM9DS0Register(0x37, self.G_I2C_ADDR, self)
        self.int1_duration_g = LSM9DS0Register(0x38, self.G_I2C_ADDR, self)
        self.out_temp_l_xm = LSM9DS0Register(0x05, self.XM_I2C_ADDR, self, True)
        self.out_temp_h_xm = LSM9DS0Register(0x06, self.XM_I2C_ADDR, self, True)
        self.status_reg_m = LSM9DS0Register(0x07, self.XM_I2C_ADDR, self, True)
        self.out_x_l_m = LSM9DS0Register(0x08, self.XM_I2C_ADDR, self, True)
        self.out_x_h_m = LSM9DS0Register(0x09, self.XM_I2C_ADDR, self, True)
        self.out_y_l_m = LSM9DS0Register(0x0A, self.XM_I2C_ADDR, self, True)
        self.out_y_h_m = LSM9DS0Register(0x0B, self.XM_I2C_ADDR, self, True)
        self.out_z_l_m = LSM9DS0Register(0x0C, self.XM_I2C_ADDR, self, True)
        self.out_z_h_m = LSM9DS0Register(0x0D, self.XM_I2C_ADDR, self, True)
        self.who_am_i_xm = LSM9DS0Register(0x0F, self.XM_I2C_ADDR, self, True)
        self.int_ctrl_reg_m = LSM9DS0Register(0x12, self.XM_I2C_ADDR, self)
        self.int_src_reg_m = LSM9DS0Register(0x13, self.XM_I2C_ADDR, self, True)
        self.int_ths_l_m = LSM9DS0Register(0x14, self.XM_I2C_ADDR, self)
        self.int_ths_h_m = LSM9DS0Register(0x15, self.XM_I2C_ADDR, self)
        self.offset_x_l_m = LSM9DS0Register(0x16, self.XM_I2C_ADDR, self)
        self.offset_x_h_m = LSM9DS0Register(0x17, self.XM_I2C_ADDR, self)
        self.offset_y_l_m = LSM9DS0Register(0x18, self.XM_I2C_ADDR, self)
        self.offset_y_h_m = LSM9DS0Register(0x19, self.XM_I2C_ADDR, self)
        self.offset_z_l_m = LSM9DS0Register(0x1A, self.XM_I2C_ADDR, self)
        self.offset_z_h_m = LSM9DS0Register(0x1B, self.XM_I2C_ADDR, self)
        self.reference_x = LSM9DS0Register(0x1C, self.XM_I2C_ADDR, self)
        self.reference_y = LSM9DS0Register(0x1D, self.XM_I2C_ADDR, self)
        self.reference_z = LSM9DS0Register(0x1E, self.XM_I2C_ADDR, self)
        self.ctrl_reg0_xm = LSM9DS0Register(0x1F, self.XM_I2C_ADDR, self)
        self.ctrl_reg1_xm = LSM9DS0Register(0x20, self.XM_I2C_ADDR, self)
        self.ctrl_reg2_xm = LSM9DS0Register(0x21, self.XM_I2C_ADDR, self)
        self.ctrl_reg3_xm = LSM9DS0Register(0x22, self.XM_I2C_ADDR, self)
        self.ctrl_reg4_xm = LSM9DS0Register(0x23, self.XM_I2C_ADDR, self)
        self.ctrl_reg5_xm = LSM9DS0Register(0x24, self.XM_I2C_ADDR, self)
        self.ctrl_reg6_xm = LSM9DS0Register(0x25, self.XM_I2C_ADDR, self)
        self.ctrl_reg7_xm = LSM9DS0Register(0x26, self.XM_I2C_ADDR, self)
        self.status_reg_a = LSM9DS0Register(0x27, self.XM_I2C_ADDR, self, True)
        self.out_x_l_a = LSM9DS0Register(0x28, self.XM_I2C_ADDR, self, True)
        self.out_x_h_a = LSM9DS0Register(0x29, self.XM_I2C_ADDR, self, True)
        self.out_y_l_a = LSM9DS0Register(0x2A, self.XM_I2C_ADDR, self, True)
        self.out_y_h_a = LSM9DS0Register(0x2B, self.XM_I2C_ADDR, self, True)
        self.out_z_l_a = LSM9DS0Register(0x2C, self.XM_I2C_ADDR, self, True)
        self.out_z_h_a = LSM9DS0Register(0x2D, self.XM_I2C_ADDR, self, True)
        self.fifo_ctrl_reg = LSM9DS0Register(0x2E, self.XM_I2C_ADDR, self)
        self.fifo_src_reg = LSM9DS0Register(0x2F, self.XM_I2C_ADDR, self, True)
        self.int_gen_1_reg = LSM9DS0Register(0x30, self.XM_I2C_ADDR, self)
        self.int_gen_1_src = LSM9DS0Register(0x31, self.XM_I2C_ADDR, self, True)
        self.int_gen_1_ths = LSM9DS0Register(0x32, self.XM_I2C_ADDR, self)
        self.int_gen_1_duration = LSM9DS0Register(0x33, self.XM_I2C_ADDR, self)
        self.int_gen_2_reg = LSM9DS0Register(0x34, self.XM_I2C_ADDR, self)
        self.int_gen_2_src = LSM9DS0Register(0x35, self.XM_I2C_ADDR, self, True)
        self.int_gen_2_ths = LSM9DS0Register(0x36, self.XM_I2C_ADDR, self)
        self.int_gen_2_duration = LSM9DS0Register(0x37, self.XM_I2C_ADDR, self)
        self.click_cfg = LSM9DS0Register(0x38, self.XM_I2C_ADDR, self)
        self.click_src = LSM9DS0Register(0x39, self.XM_I2C_ADDR, self, True)
        self.click_ths = LSM9DS0Register(0x3A, self.XM_I2C_ADDR, self)
        self.time_limit = LSM9DS0Register(0x3B, self.XM_I2C_ADDR, self)
        self.time_latency = LSM9DS0Register(0x3C, self.XM_I2C_ADDR, self)
        self.time_window = LSM9DS0Register(0x3D, self.XM_I2C_ADDR, self)
        self.act_ths = LSM9DS0Register(0x3E, self.XM_I2C_ADDR, self)
        self.act_dur = LSM9DS0Register(0x3F, self.XM_I2C_ADDR, self)

    def __enter__(self):
        self = super().__enter__()
        self.verify_whoami()
        return self

    def verify_whoami(self):
        assert(self.who_am_i_xm.get() == 0x49)
        assert(self.who_am_i_g.get() == 0xD4)

    def enable_temperature(self):
        self.ctrl_reg5_xm.set(self.ctrl_reg5_xm.get() | TEMP_EN)

    def get_temperature(self):
        t_low, t_high = self.out_temp_l_xm.get_bulk(2)
        return twos_complement((t_high << 8) | t_low, 12)

    def setup_interrupts(self):
        # interrupts
        # CTRL_REG3
        # ctrl_reg3_value = 0
        # self.ctrl_reg3_xm.set(ctrl_reg3_value)
        # CTRL_REG4
        # ctrl_reg4_value = 0
        # self.ctrl_reg4_xm.set(ctrl_reg4_value)
        raise NotImplementedError()

    def setup_accelerometer(self,
                            fifo_enable=False,
                            fifo_watermark_enable=False,
                            high_pass_filter_enable=False,
                            data_rate=100,
                            continious_update=True,
                            x_enable=True,
                            y_enable=True,
                            z_enable=True,
                            anti_alias_filter_bandwidth=773,
                            full_scale=2,
                            self_test='normal',
                            high_pass_filter_mode='normalreset',
                            filtered_data_selection=False):
        # CTRL_REG0
        ctrl_reg0_value = 0
        if fifo_enable:
            ctrl_reg0_value |= 1 << 6
        if fifo_watermark_enable:
            ctrl_reg0_value |= 1 << 5
        if high_pass_filter_enable:
            ctrl_reg0_value |= 1 << 2
        self.ctrl_reg0_xm.set(ctrl_reg0_value)

        # CTRL_REG1
        ctrl_reg1_value = 0
        acceleration_data_rates = {0: 0b0000 << 4,
                                   3.125: 0b0001 << 4,
                                   6.25: 0b0010 << 4,
                                   12.5: 0b0011 << 4,
                                   25: 0b0100 << 4,
                                   50: 0b0101 << 4,
                                   100: 0b0110 << 4,
                                   200: 0b0111 << 4,
                                   400: 0b1000 << 4,
                                   800: 0b1001 << 4,
                                   1600: 0b1010 << 4}
        if data_rate in acceleration_data_rates:
            ctrl_reg1_value |= acceleration_data_rates[data_rate]
        if not continious_update:
            ctrl_reg1_value |= 1 << 3
        if z_enable:
            ctrl_reg1_value |= 1 << 2
        if y_enable:
            ctrl_reg1_value |= 1 << 1
        if x_enable:
            ctrl_reg1_value |= 1
        self.ctrl_reg1_xm.set(ctrl_reg1_value)

        # CTRL_REG2
        ctrl_reg2_value = 0
        aaafb = {773: 0b00 << 5,
                 194: 0b01 << 5,
                 362: 0b10 << 5,
                 50: 0b11 << 5}
        if anti_alias_filter_bandwidth in aaafb:
            ctrl_reg2_value |= aaafb[anti_alias_filter_bandwidth]
        fss = {2: 0b000 << 3,
               4: 0b001 << 3,
               6: 0b010 << 3,
               8: 0b011 << 3,
               16: 0b100 << 3}
        if full_scale in fss:
            ctrl_reg2_value |= fss[full_scale]
            self._accelerometer_full_scale = full_scale
        st = {'normal': 0b00 << 1,
              'positive': 0b01 << 1,
              'negative': 0b10 << 1}
        if self_test in st:
            ctrl_reg2_value |= st[self_test]
        self.ctrl_reg2_xm.set(ctrl_reg2_value)

        # CTRL_REG7
        ctrl_reg7_value = 0
        high_pass_filter_modes = {'normalreset': 0b00 << 6,
                                  'reference': 0b01 << 6,
                                  'normal': 0b10 << 6,
                                  'autoreset': 0b11 << 6}
        if high_pass_filter_mode in high_pass_filter_modes:
            ctrl_reg7_value |= high_pass_filter_modes[high_pass_filter_mode]
        if filtered_data_selection:
            ctrl_reg7_value |= 1 << 5
        # do not disturb other half of CTRL_REG7
        ctrl_reg7_value |= self.ctrl_reg7_xm.get() & 0x1F
        self.ctrl_reg7_xm.set(ctrl_reg7_value)

    def setup_magnetometer(self,
                           temperature_sensor_enable=True,
                           high_resolution=False,
                           data_rate=25,
                           latch_interrupt_request_2=False,
                           latch_interrupt_request_1=False,
                           full_scale=4,
                           low_power=False,
                           sensor_mode='single'):
        # CTRL_REG5
        ctrl_reg5_value = 0
        if temperature_sensor_enable:
            ctrl_reg5_value |= 1 << 7
        if high_resolution:
            ctrl_reg5_value |= 0b11 << 5
        data_rates = {3.125: 0b000 << 2,
                      6.25: 0b001 << 2,
                      12.5: 0b010 << 2,
                      25: 0b011 << 2,
                      50: 0b100 << 2,
                      100: 0b101 << 2}
        if data_rate in data_rates:
            ctrl_reg5_value |= data_rates[data_rate]
        if latch_interrupt_request_2:
            ctrl_reg5_value |= 1 << 1
        if latch_interrupt_request_1:
            ctrl_reg5_value |= 1
        self.ctrl_reg5_xm.set(ctrl_reg5_value)

        # CTRL_REG6
        ctrl_reg6_value = 0
        full_scales = {2: 0b00 << 5,
                       4: 0b01 << 5,
                       8: 0b10 << 5,
                       12: 0b11 << 5}
        if full_scale in full_scales:
            ctrl_reg6_value |= full_scales[full_scale]
            self._magnetometer_full_scale = full_scale
        self.ctrl_reg6_xm.set(ctrl_reg6_value)

        # CTRL_REG7
        ctrl_reg7_value = 0
        if low_power:
            ctrl_reg7_value |= 1 << 2
        sensor_modes = {'continious': 0b00,
                        'single': 0b01,
                        'powerdown': 0b10}
        if sensor_mode in sensor_modes:
            ctrl_reg7_value |= sensor_modes[sensor_mode]
        # do not disturb other half of CTRL_REG7
        ctrl_reg7_value |= self.ctrl_reg7_xm.get() & 0xF8
        self.ctrl_reg7_xm.set(ctrl_reg7_value)

    def setup_gyroscope(self,
                        data_rate=95,
                        cutoff_selection=0,
                        power_down=False,
                        x_enable=True,
                        y_enable=True,
                        z_enable=True,
                        high_pass_filter_mode='normalreset',
                        high_pass_filter_cutoff_selection=0,
                        continious_update=True,
                        big_endian=False,
                        full_scale=245,
                        self_test_mode='normal',
                        reboot_memory_content=False,
                        fifo_enable=False,
                        high_pass_filter_enable=False,
                        int1_selection=0,
                        out_selection=0):
        # CTRL_REG1
        ctrl_reg1_value = 0
        data_rates = {95: 0b00 << 6,
                      190: 0b01 << 6,
                      380: 0b10 << 6,
                      760: 0b11 << 6}
        if data_rate in data_rates:
            ctrl_reg1_value |= data_rates[data_rate]
        if cutoff_selection in range(4):
            ctrl_reg1_value |= cutoff_selection << 4
        if not power_down:
            ctrl_reg1_value |= 1 << 3
        if z_enable:
            ctrl_reg1_value |= 1 << 2
        if y_enable:
            ctrl_reg1_value |= 1 << 1
        if x_enable:
            ctrl_reg1_value |= 1
        self.ctrl_reg1_g.set(ctrl_reg1_value)

        # CTRL_REG2
        ctrl_reg2_value = 0
        high_pass_filter_modes = {'normalreset': 0b00 << 4,
                                  'reference': 0b01 << 4,
                                  'normal': 0b10 << 4,
                                  'autoreset': 0b11 << 4}
        if high_pass_filter_mode in high_pass_filter_modes:
            ctrl_reg2_value |= high_pass_filter_modes[high_pass_filter_mode]
        if high_pass_filter_cutoff_selection in range(10):
            ctrl_reg2_value |= high_pass_filter_cutoff_selection
        self.ctrl_reg2_g.set(ctrl_reg2_value)

        # CTRL_REG3 (interrupt stuff)
        ctrl_reg3_value = 0
        self.ctrl_reg3_g.set(ctrl_reg3_value)

        # CTRL_REG4
        ctrl_reg4_value = 0
        if not continious_update:
            ctrl_reg4_value |= 1 << 7
        if big_endian:
            ctrl_reg4_value |= 1 << 6
        full_scales = {245: 0b00 << 4,
                       500: 0b01 << 4,
                       2000: 0b10 << 4}
        if full_scale in full_scales:
            ctrl_reg4_value |= full_scales[full_scale]
            self._gyroscope_full_scale = full_scale
        self_test_modes = {'normal': 0b00 << 1,
                           'selftest0': 0b01 << 1,
                           'selftest1': 0b11 << 1}
        if self_test_mode in self_test_modes:
            ctrl_reg4_value |= self_test_modes[self_test_mode]
        # SPI mode (bit 0) is obviously disabled since this is an I2C module
        self.ctrl_reg4_g.set(ctrl_reg4_value)

        # CTRL_REG5
        ctrl_reg5_value = 0
        if reboot_memory_content:
            ctrl_reg5_value |= 1 << 7
        if fifo_enable:
            ctrl_reg5_value |= 1 << 6
        if high_pass_filter_enable:
            ctrl_reg5_value |= 1 << 4
        if int1_selection in range(4):
            ctrl_reg5_value |= int1_selection << 2
        if out_selection in range(4):
            ctrl_reg5_value |= out_selection
        self.ctrl_reg5_g.set(ctrl_reg5_value)

        ctrlregs = self.ctrl_reg1_g.get_bulk(5)
        for i in range(5):
            print("CTRL_REG{}_G: {}".format(i+1, hex(ctrlregs[i])))

    def _get_twos_complement_xyz(self, register):
        xlo, xhi, ylo, yhi, zlo, zhi = register.get_bulk(6)
        v = {'x': xhi << 8 | xlo, 'y': yhi << 8 | ylo, 'z': zhi << 8 | zlo}
        return {axis: twos_complement(magnitude, 16)
                for axis, magnitude in v.items()}

    def _scale(self, magnitude, scale):
        return magnitude / 2**15 * scale

    def get_accelerometer(self, raw=False):
        acceleration_vector = self._get_twos_complement_xyz(self.out_x_l_a)
        if raw:
            return acceleration_vector
        else:
            return {axis: self._scale(magnitude,
                                      self._accelerometer_full_scale)
                    for axis, magnitude in acceleration_vector.items()}

    def get_magnetometer(self, raw=False):
        magnetic_vector = self._get_twos_complement_xyz(self.out_x_l_m)
        if raw:
            return magnetic_vector
        else:
            return {axis: self._scale(magnitude, self._magnetometer_full_scale)
                    for axis, magnitude in magnetic_vector.items()}

    def get_gyroscope(self, raw=False):
        gyro_vector = self._get_twos_complement_xyz(self.out_x_l_g)
        if raw:
            return gyro_vector
        else:
            return {axis: self._scale(magnitude, self._gyroscope_full_scale)
                    for axis, magnitude in gyro_vector.items()}


class LSM9DS0Register(object):

    def __init__(self,
                 register_address,
                 device_address,
                 i2c_master,
                 read_only=False):
        self.register_address = register_address
        self.device_address = device_address
        self.i2c_master = i2c_master
        self.read_only = read_only

    def get(self):
        return self.i2c_master.transaction(
            writing_bytes(self.device_address, self.register_address),
            reading(self.device_address, 1))[0][0]

    def get_bulk(self, num_registers):
        """Returns many registers starting from (and including) this one.
        Returns registers in byte format, access using indexes.
        """
        RAAI = 0x80  # Register Address Auto Increment
        return self.i2c_master.transaction(
            writing_bytes(self.device_address, RAAI | self.register_address),
            reading(self.device_address, num_registers))[0]

    def set(self, v):
        if self.read_only:
            raise LSM9DS0RegisterReadOnlyError(
                "Register at address {} is read only".format(
                    hex(register_address)))
        else:
            self.i2c_master.transaction(
                writing_bytes(self.device_address, self.register_address, v))


def twos_complement(value, bits):
    """Signs a value with an arbitary number of bits."""
    if value >= (1 << (bits - 1)):
        value = -((~value + 1) + (1 << bits))
    return value
