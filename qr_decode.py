import cv2
import numpy as np

INPUT = "captured.mp4"   
HEADER = b"STEGO|"
GRID_N = 12
CELL_PAD = 4
GRID_SCALE = 0.45


def find_center_grid(frame):
    h, w = frame.shape[:2]
    side = int(min(w, h) * GRID_SCALE)
    cell = (side - (GRID_N + 1) * CELL_PAD) // GRID_N
    grid_w = cell * GRID_N + (GRID_N + 1) * CELL_PAD
    x0 = (w - grid_w) // 2
    y0 = (h - grid_w) // 2
    return x0, y0, cell


def sample_grid(frame, x0, y0, cell):
    vals = []
    for r in range(GRID_N):
        for c in range(GRID_N):
            bx = x0 + CELL_PAD + c * (cell + CELL_PAD)
            by = y0 + CELL_PAD + r * (cell + CELL_PAD)
            patch = frame[by:by+cell, bx:bx+cell]
            if patch.size == 0:
                vals.append(0.0)
            else:
                vals.append(float(np.mean(cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY))))
    return np.array(vals, dtype=np.float32)


def bits_from_values(vals):
  
    mn = vals.min()
    mx = vals.max()
    if mx - mn < 1e-3:
        return None
    thresh = (mn + mx) / 2.0
    bits = (vals > thresh).astype(np.uint8)
    return bits


def bits_to_bytes(bits_arr):
    nbits = len(bits_arr)
    nbytes = nbits // 8
    bits_arr = bits_arr[:nbytes*8]
    if nbytes == 0:
        return b""
    byte_vals = np.packbits(bits_arr)
    return byte_vals.tobytes()


def decode():
    cap = cv2.VideoCapture(INPUT)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {INPUT}")

    
    frames = []
    max_frames = 90  
    count = 0
    while count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        count += 1
    cap.release()

    if len(frames) == 0:
        print("No frames read.")
        return


    x0, y0, cell = find_center_grid(frames[0])
    samps = []
    for f in frames:
        vals = sample_grid(f, x0, y0, cell)
        samps.append(vals)
    samps = np.vstack(samps)  
    mean_vals = np.median(samps, axis=0) 

    bits = bits_from_values(mean_vals)
    if bits is None:
        print("No contrast found.")
        return

    data = bits_to_bytes(bits)
    idx = data.find(HEADER)
    if idx == -1:
        print("HEADER not found. First bytes (hex):", data[:32].hex())
        return

    start = idx + len(HEADER)
    if start >= len(data):
        print("Header found but no length byte.")
        return
    length = data[start]
    msg = data[start+1:start+1+length].decode("utf-8", errors="ignore")
    print("DECODED:", msg)


if __name__ == "__main__":
    decode()
