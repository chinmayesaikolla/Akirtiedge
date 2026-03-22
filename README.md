Akritiedge — Shadow Contour to DXF
An OpenCV pipeline running on Raspberry Pi that detects object shadow contours and exports them as DXF files for laser cutting. No manual tracing needed.
This started as a team project for LAM Research Challenge 2024 — we made it to the finalist round. More than the competition result, it was genuinely fun to build and gave me solid hands-on practice with image processing.

What it does
Place an object on a matte surface under controlled lighting. The camera captures the shadow, OpenCV detects the contour, a nesting algorithm arranges it on the sheet, and a DXF file gets exported — ready for the laser cutter.
We generated 50+ DXF files during testing. What used to take manual tracing now takes one button press.

Pipeline
Camera → Shadow capture → Grayscale + Threshold
→ Contour detection → Offset + corner processing
→ Nesting → DXF export
Parameters like offset distance and corner style (sharp vs rounded) are adjustable from the UI — operators don't need to touch the code.

Hardware

Raspberry Pi
720p USB camera (mounted overhead on acrylic rig)
Controlled directional lighting
Matte non-reflective background
<img width="1406" height="833" alt="image" src="https://github.com/user-attachments/assets/793a7239-8fb8-40f8-9c93-0af41d21b31b" />
Setup
bashpip install opencv-python ezdxf numpy
python main.py

What I took from this
Decent grounding in contour detection and image thresholding under real (imperfect) lighting conditions. Also my first proper team project — coordinating code, hardware setup, and presentation with teammates across a tight deadline.

Built at VFSTR · Sep–Oct 2024 · LAM Research Challenge 2024
