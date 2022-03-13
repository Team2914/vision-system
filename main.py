import sys
sys.path.insert(1, 'roboflow-edge-infer/')
from RoboflowInfer import OAKThread, devices
import cv2
import time
from networktables import NetworkTables

size = (740, 416)

def connect_tables():
    NetworkTables.initialize(server="10.29.14.2")

def on_target(thread, detections, frame, raw_frame):
    if len(detections) > 0 and NetworkTables.isConnected():
        x_tot = 0
        y_tot = 0
        height = 0

        for det in detections:
            x_tot = x_tot + (det[2] + det[0])/2
            y_tot = y_tot + (det[3] + det[1])/2
            

        x_avg = x_tot/len(detections)
        y_avg = y_tot/len(detections)
        height_avg = height/len(detections)

        NetworkTables.getTable("Target").putNumber("target_tracking", 1)
        NetworkTables.getTable("Target").putNumber("target_x", (x_avg-(size[0]/2))/size[0])
        NetworkTables.getTable("Target").putNumber("target_y", (y_avg-(size[1]/2))/size[1])
        NetworkTables.getTable("Target").putNumber("target_height", height_avg)

    elif NetworkTables.isConnected():
        NetworkTables.getTable("Target").putNumber("target_tracking", 0)

    else:
        connect_tables()

def to_aiming(d):
    print(d)
    res = [
        str(((d[2]-d[0])-(size[0]/2))/size[0]),str(((d[3]-d[1])-(size[1]/2))/size[1]), str((d[2]-d[0])), str((size[0]/2))
    ]
    return res

def on_ball(thread, detections, frame, raw_frame):
    blue = []
    red = []

    for det in detections:
        if det[4] == "blue":
            blue.append(",".join(to_aiming(det)))
        else:
            red.append(",".join(to_aiming(det)))

    print(blue, red)
    if len(detections) > 0 and NetworkTables.isConnected():
        NetworkTables.getTable("Balls").putStringArray("blue", blue)
        NetworkTables.getTable("Balls").putStringArray("red", red)


    elif NetworkTables.isConnected():
        NetworkTables.getTable("Balls").putStringArray("blue", [])
        NetworkTables.getTable("Balls").putStringArray("red", [])

    else:
        connect_tables()

if __name__ == '__main__':
    print(devices())
    rf1 = OAKThread(1, "Detect-1", 1, on_target, "rapid-react-target", "4", api_key="vf99FOKNvqSqONChPKvD", rgb=True, device="14442C1041F8AACE00", blocking=True)
    rf2 = OAKThread(2, "Detect-2", 2, on_ball, "rapid-react-balls-wzzxa", "7", api_key="vf99FOKNvqSqONChPKvD", rgb=True, device="14442C106107C0D200", blocking=True)

    rf1.start()
    rf2.start()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
