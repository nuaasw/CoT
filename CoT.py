import datetime as dt
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
import socket
import logging

logger = logging.getLogger("django")

ID = {
    "pending": "p",
    "unknown": "u",
    "assumed-friend": "a",
    "friend": "f",
    "neutral": "n",
    "suspect": "s",
    "hostile": "h",
    "joker": "j",
    "faker": "f",
    "none": "o",
    "other": "x"
}
DIM = {
    "space": "P",
    "air": "A",
    "land-unit": "G",
    "land-equipment": "G",
    "land-installation": "G",
    "sea-surface": "S",
    "sea-subsurface": "U",
    "subsurface": "U",
    "other": "X"
}

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"



class CursorOnTarget:

    def atoms(__self, unit):
        timer = dt.datetime
        now = timer.utcnow()
        zulu = now.strftime(DATETIME_FMT)
        stale_part = now.minute + 1
        if stale_part > 59:
            stale_part = stale_part - 60
        stale_now = now.replace(minute=stale_part)
        stale = stale_now.strftime(DATETIME_FMT)

        unit_id = ID[unit["identity"]] or ID["none"]
    
        cot_type = "a-" + unit_id + "-" + DIM[unit["dimension"]]

        if "type" in unit:
          cot_type = cot_type + "-" + unit["type"]

        if "uid" in unit:
          cot_id = unit["uid"]
        else:
          cot_id = uuid.uuid4().get_hex()

        evt_attr = {
            "version": "2.0",
            "uid": cot_id,
            "time": zulu,
            "start": zulu,
            "stale": stale,
            "type": cot_type
        }

        pt_attr = {
            "lat": str(unit["lat"]),
            "lon": str(unit["lon"]),
            "hae": "0",   #unit["hae"],
            "ce": "10",   #unit["ce"],
            "le": "10"    #unit["le"],
        }
        #nineLine ip
        ip_attr = {
            "ipLat":"23.5",
            "ipLon":"123.5",
            "ipHae":"200",
            "ipDis":"23.5km",
            "ipThg":"134.5"
        }

        #nineLine tgtInfo
        tgtInfo_attr = {
            "tgtDescription":"运动坦克"
        }

        #nineLine mark
        mark_attr = {
            "typeMark":"激光",
            "code":"1-1"
        }

        #nineLine friendlies
        friendlies_attr = {
            "direction":"35",
            "distance":"65km"
        }

        #nineLine egress
        egress_attr = {
            "epLat":"23.7",
            "epLon":"134.5",
            "epHae":"2000",
            "direction":"北"
        }


        #nineLine markType
        # CoT XML文件生成
        # 创建根节点
        root = ET.Element('event', attrib=evt_attr)
        # tree = ET.ElementTree(root)

        detail = ET.SubElement(root, 'detail')
        nineLine = ET.SubElement(detail,'nineLine')
        #line1-line3
        ip = ET.SubElement(nineLine,'ip',attrib=ip_attr)
        #line5
        tgtInfo = ET.SubElement(nineLine,'tgtInfo',attrib=tgtInfo_attr)
        #line7
        mark = ET.SubElement(nineLine,'mark',attrib=mark_attr)
        #line8
        friendlies = ET.SubElement(nineLine,'friendlies',attrib=friendlies_attr)
        #line9
        egress = ET.SubElement(nineLine,'egress',attrib=egress_attr)


        point = ET.SubElement(root,'point', attrib=pt_attr)

        # tree = ET.ElementTree(root)
        # __self.__indent(root)

        cot_xml = '<?xml version="1.0" standalone="yes"?>' + ET.tostring(root).decode()


        # CoT XML文件保存
        fp = open('cot.xml', 'w')
        # fp.write(cot_xml)
        # encoding = ""
        dom = minidom.parseString(cot_xml)
        dom.writexml(fp, addindent="",newl= "\n")

        cot_xml = cot_xml.encode("UTF-8")

        # cot_xml = ET.tostring(cot)
        return cot_xml

    def pushUDP(__self, ip_address, port, cot_xml):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sent = sock.sendto(cot_xml, (ip_address, port))
        # print("hello")
        return sent

    def pushTCP(__self, ip_address, port, cot_xml):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = sock.connect((ip_address, port))
        return sock.send(cot_xml)

