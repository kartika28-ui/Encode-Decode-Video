import cv2
import numpy as np

print("Extractor started...")

INPUT_VIDEO = "encoded_fixed.mp4"
SECRET_MESSAGE_LENGTH = 3
DELTA_THRESHOLD = 0


def extract_bit(dct_block):
    value = dct_block[3, 2]
    return 1 if value > DELTA_THRESHOLD else 0


def bits_to_text(bits):
    bits = np.array(bits, dtype=np.uint8)
    packed = np.packbits(bits)
    return packed.tobytes().decode("utf-8", errors="ignore")


def extract_hidden_text():
    cap = cv2.VideoCapture(INPUT_VIDEO)
    print("Video opened:", cap.isOpened())

    all_bits = []
    frame_count = 0

    # Read ONLY 1 frame for now (to avoid 150M DCT ops)
    while frame_count < 1:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        print("Processing frame:", frame_count)

        # Convert to YCrCb
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        Y = ycrcb[:, :, 0].astype(np.float32)

        h, w = Y.shape

        for row in range(0, h, 8):
            for col in range(0, w, 8):

                block = Y[row:row+8, col:col+8]

                if block.shape != (8, 8):
                    continue

                dct_block = cv2.dct(block)
                bit = extract_bit(dct_block)
                all_bits.append(bit)

    cap.release()

    print("Total frames read:", frame_count)
    print("Total bits captured:", len(all_bits))

    text = bits_to_text(all_bits)
    recovered = text[:SECRET_MESSAGE_LENGTH]
    print("Extracted hidden text:", recovered)


extract_hidden_text()
