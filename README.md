# Encode-Decode-Video

<img src="https://github.com/kartika28-ui/Encode-Decode-Video/blob/main/qr-encode-decode-png" width="700"/>

# Approach 1 - DCT-based Steganography (embed.py + extract.py)

Tried to hide bits of text inside the DCT coefficients of video frames.

**What worked:**

- Encoding inside a digital video that stays on the laptop → worked.
- Extracting directly from the encoded .mp4 (without using a phone camera) → also works.

**What failed:**

- When recording the video on a phone camera, extraction fails.
- Phone recording changes everything:
- Resolution
- Compression
- Color space
- Blocks shift
- Motion blur
- HEVC/h264 re-encoding

Because of this, the hidden DCT bits don’t survive.
So the DCT method is fine for direct digital-to-digital testing but not good when the video is re-filmed with a phone.

# Approach 2 - Visual QR-Style Grid (qr_encode.py + qr_decode.py)

Instead of hiding bits inside the frame mathematically, show a big pixel grid on screen for the first few seconds (similar to a very simple QR code), record it with a phone, and then decode the grid later.

**What worked:**

- The grid is actually visible in the recorded video.
- The decoder can read brightness values and try to rebuild bits.

**Where it still struggles:**

- Phone compression + screen glare shifts brightness
- The threshold between white/black gets messy
- Some videos showed garbage output
- Lighting/angle/exposure affects results a lot

This method is more reliable than DCT, but still not perfect unless the recording is clean and stable.
