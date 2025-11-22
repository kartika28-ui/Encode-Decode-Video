import cv2
import numpy as np

cap = cv2.VideoCapture("input.mp4")
print("isOpened:", cap.isOpened())

INPUT_VIDEO = "input_fixed.mp4"
OUTPUT_VIDEO = "encoded.mp4"
SECRET_TEXT = "123"
REPEAT_FRAMES = 30
DELTA = 10

def text_to_bits(text):
    byte_arr = text.encode("utf-8")
    bits = np.unpackbits(np.frombuffer(byte_arr, dtype=np.uint8))
    return bits

def embed_secret():
    bits = text_to_bits(SECRET_TEXT)
    bit_index = 0
    
    cap = cv2.VideoCapture(INPUT_VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (w,h))
    
    frame_no = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        Y = ycrcb[:, :, 0].astype(np.float32)
        
        if frame_no < REPEAT_FRAMES:
            for row in range(0, h, 8):
                for col in range(0,w,8):
                    if bit_index >= len(bits):
                        bit_index = 0
                    block = Y[row:row+8, col:col+8]
                    
                    dct_block = cv2.dct(block)
                    
                    if bits[bit_index] == 1:
                        dct_block[3,2] += DELTA
                    else:
                        dct_block[3,2] -= DELTA
                    
                    bit_index += 1
                    
                    Y[row:row+8, col:col+8] = cv2.idct(dct_block)
        
        ycrcb[:, :, 0] = np.clip(Y, 0, 255).astype(np.uint8)
        
        final_frame = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        
        out.write(final_frame)
        frame_no += 1
        
    cap.release()
    out.release()
    print("DONE! Encoded video saved as: ", OUTPUT_VIDEO) 
    
embed_secret()   
    
                        