import cv2
import numpy as np

INPUT = "input.mp4"               
OUTPUT = "encoded_qr.mp4"
SECRET = "123"
HEADER = "STEGO|"

GRID_N = 12           
CELL_PAD = 4          
GRID_SCALE = 0.45     
SHOW_SECONDS = 3      

def text_to_bits(s: str) -> np.ndarray:
    payload = (HEADER + chr(len(s)) + s).encode("utf-8")
    arr = np.frombuffer(payload, dtype=np.uint8)
    bits = np.unpackbits(arr)
    return bits


def draw_grid_image(frame_w, frame_h, bits):
    side = int(min(frame_w, frame_h) * GRID_SCALE)
    cell = (side - (GRID_N + 1) * CELL_PAD) // GRID_N
    grid_w = cell * GRID_N + (GRID_N + 1) * CELL_PAD

    x0 = (frame_w - grid_w) // 2
    y0 = (frame_h - grid_w) // 2

    grid = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
    bit_index = 0
    total_cells = GRID_N * GRID_N
   
    for r in range(GRID_N):
        for c in range(GRID_N):
            bx = x0 + CELL_PAD + c * (cell + CELL_PAD)
            by = y0 + CELL_PAD + r * (cell + CELL_PAD)
            if bit_index < len(bits):
                val = 255 if bits[bit_index] == 1 else 0
            else:
                val = 0
            grid[by:by+cell, bx:bx+cell] = (val, val, val)
            bit_index += 1

    return grid, (x0, y0, cell)


def encode():
    bits = text_to_bits(SECRET)
    cap = cv2.VideoCapture(INPUT)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {INPUT}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT, fourcc, fps, (w, h))

    grid_img, grid_meta = draw_grid_image(w, h, bits)
    x0, y0, cell = grid_meta

    print(f"Encoding message '{SECRET}' → {len(bits)} bits")
    print(f"Video resolution: {w}x{h} fps={fps}")
    print("Grid size:", GRID_N, "x", GRID_N, "cell px:", cell)
    frames_show = int(max(1, SHOW_SECONDS * fps))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx < frames_show:
            
            mask = (grid_img.sum(axis=2) > 0)
            frame[mask] = grid_img[mask]
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print("DONE →", OUTPUT)


if __name__ == "__main__":
    encode()
