import json
import logger
from database import DatabaseAdapter
import traceback

class CNCParsing:
    topic = '' # 主题
    jsonobj = None # 内容
    oradb = None #oracle数据库操作对象

    def __init__(self):
        try:
            self.oradb = DatabaseAdapter()
            self.oradb.oraconnect()
        except:
            errstr = traceback.format_exc()
            logger.writeLog("CNC字段解析程序初始化失败:" + errstr)

    # 根据主题及内容使用不同的方法处理数据
    def parse(self, topic,jsonobj):
        self.topic = topic
        self.jsonobj = jsonobj
        try:
            #--------------------------机床部分-----------------------------
            #机床基础信息
            if self.topic == 'Basic':
                '''
                {"CncId":"1",
                "RunStatus":"0",
                "PoweronStatus":"0",
                "Alarm":"报警信息",
                "Time":"2020-01-22 22:53:14",
                "SpindleTemp":23.567,
                "EnvTemp":23.678,
                "CutfluTemp":23.789,
                "SliderTemp":23.891,
                "Coordinate":{"X":12.123,"Y":23.234,"Z":34.345,"B":34.345,"CS":34.345,"V":34.345}
                }
                '''
                # 给部分可选值设置默认值
                if 'Alarm' not in self.jsonobj.keys():
                    self.jsonobj['Alarm'] = ''
                if 'Coordinate' not in self.jsonobj.keys():
                    self.jsonobj['Coordinate'] = {}
                    self.jsonobj['Coordinate']['X'] = 0.0
                    self.jsonobj['Coordinate']['Y'] = 0.0
                    self.jsonobj['Coordinate']['Z'] = 0.0
                    self.jsonobj['Coordinate']['B'] = 0.0
                    self.jsonobj['Coordinate']['CS'] = 0.0
                    self.jsonobj['Coordinate']['V'] = 0.0
                #生成插入的sql语句
                sqlstr = """
                insert into BASIC_MACHINE (cncid, runstatus, poweronstatus, 
                                        alarm, time, spindletemp, envtemp, 
                                        cutflutemp, slidertemp, x_axis, y_axis, z_axis,
                                        b_axis, cs_axis, v_axis)
                values (:cncid, :runstatus, 
                        :poweronstatus, :alarm, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'), 
                        :spindletemp, :envtemp, :cutflutemp, :slidertemp, :x_axis,
                        :y_axis, :z_axis, :b_axis, :cs_axis, :v_axis)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 
                            'runstatus':self.jsonobj['RunStatus'], 'poweronstatus':self.jsonobj['PoweronStatus'], 
                            'alarm':self.jsonobj['Alarm'], 'time':self.jsonobj['Time'], 
                            'spindletemp':self.jsonobj['SpindleTemp'], 'envtemp':self.jsonobj['EnvTemp'], 
                            'cutflutemp':self.jsonobj['CutfluTemp'], 'slidertemp':self.jsonobj['SliderTemp'], 
                            'x_axis':self.jsonobj['Coordinate']['X'], 'y_axis':self.jsonobj['Coordinate']['Y'], 
                            'z_axis':self.jsonobj['Coordinate']['Z'], 'b_axis':self.jsonobj['Coordinate']['B'],
                            'cs_axis':self.jsonobj['Coordinate']['CS'], 'v_axis':self.jsonobj['Coordinate']['V']}
                # 插入数据库  
                self.oradb.insert(sqlstr, parameters)
                # print("机床基础信息写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('机床基础信息写入数据库->' + json.dumps(self.jsonobj), "database.log")
            # 主轴三向震动
            elif self.topic == 'vibration':
                '''
                该表暂时删除
                {"CncId":"1",
                "Xvibration":1.123,"Yvibration":1.123,"Zvibration":1.123,
                "XvibrationP":1.123,"YvibrationP":1.123,"ZvibrationP":1.123,
                "Time":"2020-01-22 22:53:14"
                }
                '''
                # 全是必须值无省略值
                
                #生成插入的sql语句
                sqlstr = """
                insert into MACHINE_VIBRATION (cncid, xvibration, yvibration, 
                                            zvibration, xvibrationp, yvibrationp,
                                            zvibrationp, time)
                values (:cncid, :xvibration, :yvibration, :zvibration, 
                        :xvibrationp, :yvibrationp, :zvibrationp,
                        to_date(:time, 'YYYY-MM-DD HH24:MI:SS'))
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'xvibration':self.jsonobj['Xvibration'], 
                            'yvibration':self.jsonobj['Yvibration'], 'zvibration':self.jsonobj['Zvibration'], 
                            'xvibrationp':self.jsonobj['XvibrationP'], 'yvibrationp':self.jsonobj['YvibrationP'],
                            'zvibrationp':self.jsonobj['ZvibrationP'],
                            'time':self.jsonobj['Time']}
                # 插入数据库   
                self.oradb.insert(sqlstr, parameters)
                # print("主轴三向震动写入数据库:" + json.dumps(self.jsonobj)) 
                # logger.writeLog('主轴三向震动写入数据库->' + json.dumps(self.jsonobj), "database.log")
            #刀具功率磨损值
            elif self.topic == 'Abrpower': 
                '''
                {"CncId":"1",
                "AbrPower":{"ToolNo":1,
                            "Msgl":23.234,
                            "Mssx":34.345,
                            "Msxx":20.222},
                "Time":"2020-01-22 22:53:14"
                }
                '''
                #全是必须值无省略值
                #生成插入的sql语句
                sqlstr = """
                insert into MACHINE_POWER (cncid, time, abrpower,
                                        toolno, msgl, mssx, msxx)
                values (:cncid, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'),
                        :abrpower, :toolno, :msgl, :mssx, :msxx)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'time':self.jsonobj['Time'],
                            'abrpower':json.dumps(self.jsonobj['AbrPower']),
                            'toolno':self.jsonobj['AbrPower']['ToolNo'],
                            'msgl':self.jsonobj['AbrPower']['Msgl'],
                            'mssx':self.jsonobj['AbrPower']['Mssx'],
                            'msxx':self.jsonobj['AbrPower']['Msxx']}
                # 插入数据库
                self.oradb.insert(sqlstr, parameters)
                # print("刀具功率磨损值写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('刀具功率磨损值写入数据库->' + json.dumps(self.jsonobj), "database.log")
            #主轴方向加速度振动磨损值接口
            elif self.topic.find('Abracceleration') != -1:
                '''
                    {"CncId":"1",
                    "AbrAcceleration":{"ToolNo":1,
                                    "Mszd":23.234,
                                    "Mssx":34.345,
                                    "Msxx":20.222},
                    "Time":"2020-01-22 22:53:14"
                    }
                '''
                #主轴X方向加速度振动磨损值接口
                if self.topic.find('XAbracceleration') != -1:
                    self.jsonobj['direction'] = 'X'
                #主轴Y方向加速度振动磨损值接口
                elif self.topic.find('YAbracceleration') != -1:
                    self.jsonobj['direction'] = 'Y'
                #主轴Z方向加速度振动磨损值接口
                elif self.topic.find('ZAbracceleration') != -1:
                    self.jsonobj['direction'] = 'Z'
                else:
                    logger.writeLog('未发现正确的主轴方向加速度->' + json.dumps(self.jsonobj))
                    self.jsonobj['direction'] = ''
                #全是必须值无省略值
                #生成插入的sql语句
                sqlstr = """
                insert into ABRACCELERATION (cncid, time, toolno,
                                            direction, mszd, mssx,
                                            msxx)
                values (:cncid, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'),
                        :toolno, :direction, :mszd, :mssx, :msxx)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'time':self.jsonobj['Time'],
                            'toolno':self.jsonobj['AbrAcceleration']['ToolNo'],
                            'direction':self.jsonobj['direction'],
                            'mszd':self.jsonobj['AbrAcceleration']['Mszd'],
                            'mssx':self.jsonobj['AbrAcceleration']['Mssx'],
                            'msxx':self.jsonobj['AbrAcceleration']['Msxx']}
                # 插入数据库
                self.oradb.insert(sqlstr, parameters)
                # print("主轴方向加速度振动磨损写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('主轴方向加速度振动磨损写入数据库->' + json.dumps(self.jsonobj), "database.log")

            #主轴方向速度振动磨损值接口
            elif self.topic.find('Abrvelocity') != -1:
                '''
                {"CncId":"1",
                "AbrVelocity":{"ToolNo":1,
                                "Mszd":23.234,
                                "Mssx":34.345,
                                "Msxx":20.222},
                "Time":"2020-01-22 22:53:14"}
                '''
                #主轴X方向速度振动磨损值接口
                if self.topic.find('XAbrvelocity') != -1:
                    self.jsonobj['direction'] = 'X'
                #主轴Y方向速度振动磨损值接口
                elif self.topic.find('YAbrvelocity') != -1:
                    self.jsonobj['direction'] = 'Y'
                #主轴Z方向速度振动磨损值接口
                elif self.topic.find('ZAbrvelocity') != -1:
                    self.jsonobj['direction'] = 'Z'
                else:
                    logger.writeLog('未发现正确的主轴方向速度振动磨损值->' + json.dumps(self.jsonobj))
                    self.jsonobj['direction'] = ''
                #全是必须值无省略值
                #生成插入的sql语句
                sqlstr = """
                insert into ABRVELOCITY (cncid, time, toolno,
                                            direction, mszd, mssx,
                                            msxx)
                values (:cncid, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'),
                        :toolno, :direction, :mszd, :mssx, :msxx)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'time':self.jsonobj['Time'],
                            'toolno':self.jsonobj['AbrVelocity']['ToolNo'],
                            'direction':self.jsonobj['direction'],
                            'mszd':self.jsonobj['AbrVelocity']['Mszd'],
                            'mssx':self.jsonobj['AbrVelocity']['Mssx'],
                            'msxx':self.jsonobj['AbrVelocity']['Msxx']}
                # 插入数据库
                self.oradb.insert(sqlstr, parameters)
                # print("主轴方向速度振动磨损写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('主轴方向速度振动磨损写入数据库->' + json.dumps(self.jsonobj), "database.log")
            #热机时加速度有效值接口
            elif self.topic == 'Machineheat':
                '''
                {"CncId":"1","MSAvePower":23.234,"XSMedPower":34.345,"YSMedPower":20.222,
                "ZSMedPower":21.234,"BSMedPower":21.234,"VSMedPower":21.234,"MSStdPower":1,
                "XIldPower":1,"YIldPower":1,"ZIldPower":1,"BIldPower":1,"VIldPower":1,
                "MSXAccelerationMax":1,"MSYAccelerationMax":1,"XSXAccelerationMax":1,"YSYAccelerationMax":1,
                "MSXVelocityRMS":1,"MSYVelocityRMS":1,"XSXVelocityRMS":1,"YSYVelocityRMS":1,
                "MSZAccelerationMax":1,"MSZVelocityRMS":1,"Time":"2020-01-22 22:53:14"}				
                '''
                #全是必须值无省略值
                #生成插入的sql语句
                sqlstr = """
                insert into MACHINEHEAT (cncid, time, msavepower, xsmedpower, ysmedpower,
                                        zsmedpower, bsmedpower, vsmedpower, msstdpower,
                                        xildpower, yildpower, zildpower, bildpower, vildpower,
                                        msxaccelerationmax, msyaccelerationmax, mszaccelerationmax,
                                        xsxaccelerationmax, ysyaccelerationmax, msxvelocityrms, 
                                        msyvelocityrms, mszvelocityrms, xsxvelocityrms, ysyvelocityrms)
                values (:cncid, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'),
                        :msavepower, :xsmedpower, :ysmedpower,
                        :zsmedpower, :bsmedpower, :vsmedpower, :msstdpower,
                        :xildpower, :yildpower, :zildpower, :bildpower, :vildpower,
                        :msxaccelerationmax, :msyaccelerationmax, :mszaccelerationmax,
                        :xsxaccelerationmax, :ysyaccelerationmax, :msxvelocityrms, 
                        :msyvelocityrms, :mszvelocityrms, :xsxvelocityrms, :ysyvelocityrms)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'time':self.jsonobj['Time'],
                            'msavepower':self.jsonobj['MSAvePower'], 'xsmedpower':self.jsonobj['XSMedPower'],
                            'ysmedpower':self.jsonobj['YSMedPower'], 'zsmedpower':self.jsonobj['ZSMedPower'], 
                            'bsmedpower':self.jsonobj['BSMedPower'], 'vsmedpower':self.jsonobj['VSMedPower'], 
                            'msstdpower':self.jsonobj['MSStdPower'],
                            'xildpower':self.jsonobj['XIldPower'], 'yildpower':self.jsonobj['YIldPower'],
                            'zildpower':self.jsonobj['ZIldPower'], 'bildpower':self.jsonobj['BIldPower'],
                            'vildpower':self.jsonobj['VIldPower'], 
                            'msxaccelerationmax':self.jsonobj['MSXAccelerationMax'],
                            'msyaccelerationmax':self.jsonobj['MSYAccelerationMax'], 
                            'mszaccelerationmax':self.jsonobj['MSZAccelerationMax'],
                            'xsxaccelerationmax':self.jsonobj['XSXAccelerationMax'],
                            'ysyaccelerationmax':self.jsonobj['YSYAccelerationMax'], 
                            'msxvelocityrms':self.jsonobj['MSXVelocityRMS'],
                            'msyvelocityrms':self.jsonobj['MSYVelocityRMS'],
                            'mszvelocityrms':self.jsonobj['MSZVelocityRMS'],
                            'xsxvelocityrms':self.jsonobj['XSXVelocityRMS'],
                            'ysyvelocityrms':self.jsonobj['YSYVelocityRMS']}
                # 插入数据库
                self.oradb.insert(sqlstr, parameters)
                # print("热机时加速度有效值写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('热机时加速度有效值写入数据库->' + json.dumps(self.jsonobj), "database.log")
        
            #--------------------------机械手部分-----------------
            #机械手基础信息
            elif self.topic == 'JxsBasic':
                '''
                {"CncId":"1","CncNo":"111","PartNo":"222",
                "Coordinate":{"X":12.123,"Z1":23.234,"Z2":34.345,"A1":23.234,"A2":34.345},
                "Time":"2020-01-22 22:53:14"}
                '''
                # 给部分可选值设置默认值
                if 'Coordinate' not in self.jsonobj.keys():
                    self.jsonobj['Coordinate'] = {}
                    self.jsonobj['Coordinate']['X'] = 0.0 
                    self.jsonobj['Coordinate']['Z1'] = 0.0
                    self.jsonobj['Coordinate']['Z2'] = 0.0
                    self.jsonobj['Coordinate']['A1'] = 0.0
                    self.jsonobj['Coordinate']['A2'] = 0.0
                #生成插入的sql语句
                sqlstr = """
                insert into BASIC_MACHINE_HAND (cncid, cncno, partno, x_axis, z1_axis, z2_axis, a1_axis, a2_axis, time)
                values (:cncid, :cncno, :partno, :x_axis, :z1_axis, :z2_axis, :a1_axis, :a2_axis, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'))
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'cncno':self.jsonobj['CncNo'],
                              'partno':self.jsonobj['PartNo'], 'x_axis':self.jsonobj['Coordinate']['X'],
                              'z1_axis':self.jsonobj['Coordinate']['Z1'],'z2_axis':self.jsonobj['Coordinate']['Z2'],
                              'a1_axis':self.jsonobj['Coordinate']['A1'],'a2_axis':self.jsonobj['Coordinate']['A2'],
                              'time':self.jsonobj['Time']}
                # 插入数据库  
                self.oradb.insert(sqlstr, parameters)
                # print("机械手基础信息写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('机械手基础信息写入数据库->' + json.dumps(self.jsonobj), "database.log")
            
            #机械手振动接口
            elif self.topic == 'Jxsvibration':
                '''
               {"CncId":"1","LY+vibrationP":1.123,"LY-vibrationP":1.123,
                "RY+vibrationP":1.123,"RY-vibrationP":1.123,"LY+vibration":1.123,
                "LY-vibration":1.123,"RY+vibration":1.123,"RY-vibration":1.123,
                "Time":"2020-01-22 22:53:14"}
                '''
                #给部分可选值设置默认值
                
                #生成插入的sql语句
                sqlstr = """
                insert into machine_hand_vibration (cncid, ly_upper_vibrationp, ly_down_vibrationp,
                                          ry_upper_vibrationp, ry_down_vibrationp, 
                                          ly_upper_vibration, ly_down_vibration,
                                          ry_upper_vibration, ry_down_vibration, time)
                values (:cncid, :ly_upper_vibrationp, :ly_down_vibrationp,
                        :ry_upper_vibrationp, :ry_down_vibrationp, 
                        :ly_upper_vibration, :ly_down_vibration,
                        :ry_upper_vibration, :ry_down_vibration,
                        to_date(:time, 'YYYY-MM-DD HH24:MI:SS'))
                """
                parameters = {'cncid':self.jsonobj['CncId'],
                              'ly_upper_vibrationp': self.jsonobj['LY+vibrationP'],'ly_down_vibrationp': self.jsonobj['LY-vibrationP'],
                              'ry_upper_vibrationp': self.jsonobj['RY+vibrationP'],'ry_down_vibrationp': self.jsonobj['RY-vibrationP'],
                              'ly_upper_vibration': self.jsonobj['LY+vibration'],'ly_down_vibration': self.jsonobj['LY-vibration'],
                              'ry_upper_vibration': self.jsonobj['RY+vibration'],'ry_down_vibration': self.jsonobj['RY-vibration'],
                              'time':self.jsonobj['Time']}
                # 插入数据库  
                self.oradb.insert(sqlstr, parameters)
                # print("机械手震动信息写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('机械手震动信息写入数据库->' + json.dumps(self.jsonobj), "database.log")
            
            #机械手自检上传接口
            elif self.topic == 'JxsSelftest':
                '''
                 {"CncId":"1","XPowerMax":1,"Z1PowerMax":1,"Z2PowerMax":1,
                  "A1PowerMax":1,"A2PowerMax":1,"LY+AccelerationP":1,"LY-AccelerationP":1,
                  "RY+AccelerationP":1,"RY-AccelerationP":1,"LY+AccelerationHP":1,
                  "RY+AccelerationHP":1,"LY+AccelerationLP":1,"RY+AccelerationLP":1,
                  "LY+AccelerationRMS":1,"RY+AccelerationRMS":1,"Time":"2020-01-22 22:53:14"}
                '''
                #生成插入的sql语句
                sqlstr = """
                insert into MACHINE_HAND_SELFTEST (cncid, xpowermax, z1powermax, z2powermax, 
                                        a1powermax, a2powermax, 
                                        ly_up_accelerationp, ly_dn_accelerationp,
                                        ry_up_accelerationp, ry_dn_accelerationp,
                                        ly_up_accelerationhp, ry_up_accelerationhp,
                                        ly_up_accelerationlp, ry_up_accelerationlp,
                                        ly_up_accelerationrms, ry_up_accelerationrms,
                                        time)
                values (:cncid, :xpowermax, :z1powermax, :z2powermax, 
                        :a1powermax, :a2powermax, 
                        :ly_up_accelerationp, :ly_dn_accelerationp,
                        :ry_up_accelerationp, :ry_dn_accelerationp,
                        :ly_up_accelerationhp, :ry_up_accelerationhp,
                        :ly_up_accelerationlp, :ry_up_accelerationlp,
                        :ly_up_accelerationrms, :ry_up_accelerationrms,
                        to_date(:time, 'YYYY-MM-DD HH24:MI:SS'))
                """
                parameters = {'cncid': self.jsonobj['CncId'], 'xpowermax': self.jsonobj['XPowerMax'], 
                              'z1powermax': self.jsonobj['Z1PowerMax'], 'z2powermax': self.jsonobj['Z2PowerMax'], 
                              'a1powermax': self.jsonobj['A1PowerMax'], 'a2powermax': self.jsonobj['A2PowerMax'], 
                              'ly_up_accelerationp': self.jsonobj['LY+AccelerationP'], 'ly_dn_accelerationp': self.jsonobj['LY-AccelerationP'],
                              'ry_up_accelerationp': self.jsonobj['RY+AccelerationP'], 'ry_dn_accelerationp': self.jsonobj['RY-AccelerationP'],
                              'ly_up_accelerationhp': self.jsonobj['LY+AccelerationHP'], 'ry_up_accelerationhp': self.jsonobj['RY+AccelerationHP'],
                              'ly_up_accelerationlp': self.jsonobj['LY+AccelerationLP'], 'ry_up_accelerationlp': self.jsonobj['RY+AccelerationLP'],
                              'ly_up_accelerationrms': self.jsonobj['LY+AccelerationRMS'], 'ry_up_accelerationrms': self.jsonobj['RY+AccelerationRMS'],
                              'time':self.jsonobj['Time']}
                # 插入数据库  
                self.oradb.insert(sqlstr, parameters)
                # print("机械手自检写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('机械手自检写入数据库->' + json.dumps(self.jsonobj), "database.log")

            #--------------------------其他Transfer机床数据上传--------------------------
            elif self.topic == 'Transferdata':
                '''
                {"CncId":"1","vibration1":23.234,"vibration2":23.234,"vibration3":23.234,
                 "vibration4":23.234,"vibration5":23.234,"vibration6":23.234,
                 "Temp1":30.03,"Temp2":30.03,"Temp3":30.03,"Temp4":30.03,"Temp5":30.03,
                 "Temp6":30.03,"Time":"2020-01-22 22:53:14"}
                '''
                # 给部分可选值设置默认值
                if 'vibration1' not in self.jsonobj.keys():
                    self.jsonobj['vibration1'] = 0.0
                if 'vibration2' not in self.jsonobj.keys():
                    self.jsonobj['vibration2'] = 0.0
                if 'vibration3' not in self.jsonobj.keys():
                    self.jsonobj['vibration3'] = 0.0
                if 'vibration4' not in self.jsonobj.keys():
                    self.jsonobj['vibration4'] = 0.0
                if 'vibration5' not in self.jsonobj.keys():
                    self.jsonobj['vibration5'] = 0.0
                if 'vibration6' not in self.jsonobj.keys():
                    self.jsonobj['vibration6'] = 0.0
                if 'Temp1' not in self.jsonobj.keys():
                    self.jsonobj['Temp1'] = 0.0
                if 'Temp2' not in self.jsonobj.keys():
                    self.jsonobj['Temp2'] = 0.0
                if 'Temp3' not in self.jsonobj.keys():
                    self.jsonobj['Temp3'] = 0.0
                if 'Temp4' not in self.jsonobj.keys():
                    self.jsonobj['Temp4'] = 0.0
                if 'Temp5' not in self.jsonobj.keys():
                    self.jsonobj['Temp5'] = 0.0
                if 'Temp6' not in self.jsonobj.keys():
                    self.jsonobj['Temp6'] = 0.0
                #生成插入的sql语句
                sqlstr = """
                insert into BASIC_OTHER_MACHINE (cncid, time, vibration1, vibration2,
                                                vibration3, vibration4, vibration5,
                                                vibration6, temp1, temp2, temp3, temp4,
                                                temp5, temp6)
                values (:cncid, to_date(:time, 'YYYY-MM-DD HH24:MI:SS'),
                        :vibration1, :vibration2, :vibration3, :vibration4,
                        :vibration5, :vibration6, :temp1, :temp2, :temp3, :temp4,
                        :temp5, :temp6)
                """
                parameters = {'cncid':self.jsonobj['CncId'], 'time':self.jsonobj['Time'],
                            'vibration1':self.jsonobj['vibration1'],
                            'vibration2':self.jsonobj['vibration2'],
                            'vibration3':self.jsonobj['vibration3'],
                            'vibration4':self.jsonobj['vibration4'],
                            'vibration5':self.jsonobj['vibration5'],
                            'vibration6':self.jsonobj['vibration6'],
                            'temp1':self.jsonobj['Temp1'], 'temp2':self.jsonobj['Temp2'],
                            'temp3':self.jsonobj['Temp3'], 'temp4':self.jsonobj['Temp4'],
                            'temp5':self.jsonobj['Temp5'], 'temp6':self.jsonobj['Temp6'],
                            }
                # 插入数据库
                self.oradb.insert(sqlstr, parameters)
                # print("其他Transfer机床数据写入数据库:" + json.dumps(self.jsonobj))
                # logger.writeLog('其他Transfer机床数据写入数据库->' + json.dumps(self.jsonobj), "database.log")
            else:
                logger.writeLog("传入值异常，未找到匹配项!" + json.dumps(self.jsonobj))
        except:
            errstr = traceback.format_exc()
            logger.writeLog("CNC字段解析程序失败:" + errstr + json.dumps(self.jsonobj))
        

