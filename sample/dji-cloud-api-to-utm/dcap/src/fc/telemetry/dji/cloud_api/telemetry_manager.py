# -*- coding: utf-8 -*-
"""
フライトコントローラから取得可能な情報をTelemetryとして管理し、他のプロセスへ配信する処理を行うモジュール
"""
from protocolbuffers.uas_common_pb2 import UasState
from decimal import Decimal
from fc.telemetry.dji.cloud_api.telemetry_holder import TelemetryHolder


class TelemetryManagerImpl:
    """
    Telemetry情報の管理クラスに登録する処理の実体を持つクラス
    """
    landing_status_table = {
            0: 'Standby',
            1: 'Takeoff preparation',
            2: 'Takeoff preparation completed'
    }
    # UASステータス着陸中に該当するmode_code
    operating_status_table = {
        6: 'Panoramic photography',
        7: 'Intelligent tracking',
        8: 'ADS-B avoidance',
        9: 'Auto returning to home',
        10: 'Automatic landing',
        11: 'Forced landing',
        12: 'Three-blade landing'
    }
    # UASステータス移動中に該当するmode_code
    inflight_status_table = {
        3: 'Manual flight',
    }
    # UASステータスミッション飛行中に該当するmode_code
    mission_status_table = {
        4: 'Automatic takeoff',
        5: 'Wayline flight'
    }
    # UASステータスミッション飛行中に該当するmode_code

    def __init__(self):
        """
        コンストラクタ

        """
        pass

    def convert_str_float(vale):
        """

        :param vale: 変換する値
        :return: 変換後の値
        """
        if vale is not None:
            return float(vale)
        else:
            return vale

    def snapshot(self, telemetry_dic):
        """
        Telemetry情報の管理クラスに登録する ``snapshot`` 関数の実体となるメソッド

        :return: 本メソッド実行時に取得したTelemetry情報
        """
        holder = TelemetryHolder()
        holder.system_status = telemetry_dic['mode_code']

        holder.armed = (telemetry_dic['mode_code'] != '0')
        holder.location_global_lat = telemetry_dic.get('latitude')
        holder.location_global_lon = telemetry_dic.get('longitude')
        holder.location_global_alt = telemetry_dic.get('height')
        elevation = telemetry_dic.get('elevation')
        if holder.location_global_alt is not None and elevation is not None:
            holder.location_global_relative_alt = elevation
        else:
            holder.location_global_relative_alt = holder.location_global_alt

        holder.location_global_alt_gps = telemetry_dic.get('height')
        if holder.location_global_alt_gps is not None and elevation is not None:
            holder.location_global_relative_alt_gps = elevation
        else:
            holder.location_global_relative_alt_gps = holder.location_global_alt_gps

        # degree (-180- +180) ->degree (0 - +360)
        holder.heading = telemetry_dic.get('attitude_head')
        # radian
        holder.attitude_pitch = telemetry_dic.get('attitude_pitch')
        # radian
        holder.attitude_yaw = telemetry_dic.get('attitude_head')
        # radian
        holder.attitude_roll = telemetry_dic.get('attitude_roll')
        # meter/sec
        hspeed = telemetry_dic.get('horizontal_speed')
        if hspeed is not None and holder.heading is not None:
            holder.velocity_north = 0
            holder.velocity_east = 0
            holder.speed_air = hspeed
            holder.speed_ground = hspeed
        # meter/sec
        vertical_speed = telemetry_dic.get('vertical_speed')
        if vertical_speed is not None:
            holder.velocity_ground = -1 * vertical_speed

        battery = telemetry_dic.get('battery')
        if battery is not None:
            batteries = battery.get('batteries')
            if batteries is not None:
                if len(batteries) > 0:
                    # milli volts
                    holder.battery_voltage = batteries[0].get('voltage')
                    # # milli amperes
                    holder.battery_current = None
                    # percent
                    holder.battery_level = batteries[0].get('capacity_percent')

        holder.location_home_lat = telemetry_dic.get('home_latitude')
        holder.location_home_lon = telemetry_dic.get('home_longitude')

        position_state = telemetry_dic.get('position_state')
        if position_state is not None:
            holder.gps_satellites = position_state.get('gps_number')

        if 'mission_id' in telemetry_dic:
            holder.mission_id = telemetry_dic.get('mission_id')
        else:
            holder.mission_id = None

        return holder

    def set_vehicle_telemetry(self, v_stat, uas_telemetry):
        """
        テレメトリ情報を設定するメソッド

        :param v_stat: テレメトリ情報
        :param uas_telemetry: FOS通知用テレメトリ情報
        :return FOS通知用テレメトリ情報
        """
        base_altitude_type = ''
        # UAS状態の設定
        uas_telemetry.state = x if (x := self.convert_mode_to_uas_state(v_stat.get_system_status(),
                                    v_stat.get_mission_id())) is not None else UasState.Value('LANDING')

        if v_stat.get_location_global_lat() is not None:
            uas_telemetry.lattitude.value = self.float_to_int(v_stat.get_location_global_lat(), 10000000)
        if v_stat.get_location_global_lon() is not None:
            uas_telemetry.longitude.value = self.float_to_int(v_stat.get_location_global_lon(), 10000000)
        if base_altitude_type == 'gps':
            # global location alt relative_alt_gps [meter]
            if v_stat.get_location_global_alt_gps() is not None:
                uas_telemetry.altitude.value = self.float_to_int(v_stat.get_location_global_alt_gps(), 1000)
            if v_stat.get_location_global_relative_alt_gps() is not None:
                uas_telemetry.relative_altitude.value = self.float_to_int(
                    v_stat.get_location_global_relative_alt_gps(), 1000)
        else:
            # global location alt relative_alt [meter]
            if v_stat.get_location_global_alt() is not None:
                uas_telemetry.altitude.value = self.float_to_int(v_stat.get_location_global_alt(), 1000)
            if v_stat.get_location_global_relative_alt() is not None:
                uas_telemetry.relative_altitude.value = self.float_to_int(
                    v_stat.get_location_global_relative_alt(), 1000)
        # local location [meter]
        if v_stat.get_location_local_north() is not None:
            uas_telemetry.north.value = self.float_to_int(v_stat.get_location_local_north(), 1000)
        if v_stat.get_location_local_east() is not None:
            uas_telemetry.east.value = self.float_to_int(v_stat.get_location_local_east(), 1000)
        if v_stat.get_location_local_down() is not None:
            uas_telemetry.down.value = self.float_to_int(v_stat.get_location_local_down(), 1000)
        # heading [degree] 単位はdegでFOS連携では10000000倍する予定であったが、桁あふれするため1000000倍に変更
        if v_stat.get_heading() is not None:
            uas_telemetry.heading.value = int(self.parse_0to360_degree(v_stat.get_heading()) * 1000000)
        # attitude [degree]
        if v_stat.get_attitude_pitch() is not None:
            uas_telemetry.attitude_pitch.value = self.float_to_int(v_stat.get_attitude_pitch(), 10000000)
        if v_stat.get_attitude_yaw() is not None:
            uas_telemetry.attitude_yaw.value = self.float_to_int(v_stat.get_attitude_yaw(), 10000000)
        if v_stat.get_attitude_roll() is not None:
            uas_telemetry.attitude_roll.value = self.float_to_int(v_stat.get_attitude_roll(), 10000000)
        # velocity [meter/sec]
        if v_stat.get_velocity_north() is not None:
            uas_telemetry.velocity_north.value = self.float_to_int(v_stat.get_velocity_north(), 1000)
        if v_stat.get_velocity_east() is not None:
            uas_telemetry.velocity_east.value = self.float_to_int(v_stat.get_velocity_east(), 1000)
        if v_stat.get_velocity_ground() is not None:
            uas_telemetry.velocity_ground.value = self.float_to_int(v_stat.get_velocity_ground(), 1000)
        # speed [metres/sec]
        if v_stat.get_speed_air() is not None:
            uas_telemetry.air_speed.value = self.float_to_int(v_stat.get_speed_air(), 1000)
        if v_stat.get_speed_ground() is not None:
            uas_telemetry.ground_speed.value = self.float_to_int(v_stat.get_speed_ground(), 1000)
        # battery voltage [milli volts]
        if v_stat.get_battery_voltage() is not None:
            uas_telemetry.battery_voltage.value = v_stat.get_battery_voltage()
        # battery current [milli amperes]
        if v_stat.get_battery_current() is not None:
            uas_telemetry.battery_current.value = self.float_to_int(v_stat.get_battery_current(), 1000)
        # battery level [percent]
        battery_level = v_stat.get_battery_level()
        if battery_level is not None:
            uas_telemetry.battery_level.value = int(battery_level)

        # mission id [uuid]
        if v_stat.get_mission_id() is not None:
            uas_telemetry.mission_id = v_stat.get_mission_id()

        # gps satellites num [number]
        if v_stat.get_gps_satellites() is not None:
            uas_telemetry.gps_num.value = v_stat.get_gps_satellites()
        # fc status [id]
        if v_stat.get_fc_status() is not None:
            uas_telemetry.fc_status.value = v_stat.get_fc_status()
        # next waypoint
        # if v_stat.get_next_waypoint() is not None:
        #     uas_telemetry.next_waypoint.value = v_stat.get_next_waypoint()
        # compass status
        if v_stat.get_compass_data() is not None:
            uas_telemetry.compass_status.value = v_stat.get_compass_data()

        return uas_telemetry

    def float_to_int(self, value1, value2):
        """
        floatを指定倍率で乗算してからintに変換する関数

        桁の丸め誤差防止のため、floatをDecimalに変換している。
        また有効桁数の扱いはDecimalのprec設定による。
        例えば同一スレッド内でgetcontext().prec = 16　が実行されている場合は１７桁目は切り捨てとなる。

        :param value1: float値
        :param value2: 倍率
        :return: 倍率をかけられたint値
        """
        #

        decimal_value1 = Decimal(value1)
        decimal_value2 = Decimal(value2)
        return int(decimal_value1 * decimal_value2)

    def try_minus_degree_parse(self, target):
        """
        0~360で表現された角度を~180から+180のレンジに変換を行う関数

        :param target: 変換を行う角度

        :return:　~180から+180のレンジに変換された値
        """
        target += 180
        target %= 360
        target -= 180
        return target

    def parse_0to360_degree(self, target_degree):
        """
        -180から+180で表現された角度を0~360のレンジに変換を行う関数

        :param target: 変換を行う角度

        :return:　0~360のレンジに変換された値
        """
        target_degree %= 360
        if 0 > target_degree:
            target_degree += 360
        return target_degree

    def convert_mode_to_uas_state(self, mode_code: int, mission_id: str):
        '''DJIから取得できるmode_codeを制御APのUASステータスに変換する関数

        :param mode_code: 機体のmode_code
        :return: 変換後のUASステータス
        '''

        # UAS状態の設定
        if mode_code in self.landing_status_table:
            return UasState.Value('LANDING')
        elif mode_code in self.operating_status_table:
            return UasState.Value('INFLIGHT_OPERATING')
        elif mode_code in self.inflight_status_table:
            # mission_idが存在する場合はミッション中ホバリングと判定
            if mission_id is not None:
                return UasState.Value('INFLIGHT_MISSION_HOVER')
            return UasState.Value('INFLIGHT')
        elif mode_code in self.mission_status_table:
            return UasState.Value('INFLIGHT_MISSION')
        elif mission_id is not None:
            # mode_codeが該当せずmission_idのみ存在する場合はミッション中断扱い
            return UasState.Value('INFLIGHT_MISSION_INTERRUPT')
        else:
            return None
