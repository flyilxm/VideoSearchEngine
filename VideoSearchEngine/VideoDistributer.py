import video_utils
import asyncio
import argparse
import pickle
import socket
import time

# Main file for taking a video, and separating it into multiple chunks
# and distributing the work

# Main API is here, more files may be used for the implementation

def get_video_distributor():
    '''
    return the version specified in the configuration to use
    e.g. if there is a basic one and a complex one, the configuration should be able
    to decide which one to use
    '''
    return None

'''
Describe API supported here
'''

async def mock_send_frame(frame_cluster, host, port):
    '''
    Given an array of frames send it to an listening server for further processing. Use pickle
    to serialize the array so it can be sent over the network.
    '''
    # Pickle the array of frames.
    filename = "host" + str(host) + "port" + str(port) + "distributerPickleFile.pkl"
    f = open(filename,'wb')
    pickle.dump(frame_cluster, f)
    f.close()

    # TODO: Pass in host and port should as parameters, depends on how many machines are avaliable.
    s = socket.socket()         # Create a socket object

    # Send pickle file over the network to server.
    s.connect((host, port))
    
    f = open(filename,'rb')
    data = f.read(1024)
    while (data):
        s.send(data)
        data = f.read(1024)
    f.close()
    s.close()

#TODO: Look into whether or not a sequential approach is ok or not for this.
def distribute_frames(frames, hostname, basePort, clusterSize=10):
    '''
    Given an array of frames break into subarrays and send each subarray
    to some server for processing.
    '''
    port = basePort
    loop = asyncio.get_event_loop()
    tasks = [] 
    cluster = []
    for frame in frames:
        cluster.append(frame);
        if len(cluster) % clusterSize == 0:
            print("Sending cluster")
            cluster_copy = list(cluster)
            tasks.append(asyncio.ensure_future(mock_send_frame(cluster_copy, hostname, port)))
            port = port + 1
            cluster.clear()   
    if len(cluster) != 0:
        print("Sending cluster")
        cluster_copy = list(cluster)
        tasks.append(asyncio.ensure_future(mock_send_frame(cluster_copy, hostname, port)))
        port = port + 1
        cluster.clear()
    loop.run_until_complete(asyncio.wait(tasks))  
    loop.close()

'''
Example Usage:
    python VideoDistributer.py --video_path ../clips/bunny_clip.mp4
'''

#TODO: Add arguments to: only extract every nth frame, change width/height of captured frames, etc.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument("--video_path", help="path of the video",type=str, required=True)
    args = parser.parse_args()        
    res = video_utils.get_frames_from_video(args.video_path)
    distribute_frames(res, "localhost", 24448, 51) # hard code 24448 as the port on the local host, use 51 as the cluster size since we only have two workers on the same local machine