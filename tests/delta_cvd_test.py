from color_utils import read_rgb, rgb_to_lab, deltaE_2000, simulate_cvd

# 1) Load image
img = read_rgb("../images/ishiharaTest.png")

# 2) Convert to Lab format
lab_normal = rgb_to_lab(img)

# 3) Simulate CVD
img_cvd = simulate_cvd(img, cvd_type="deutan", severity=1.0)

# 4) Convert CVD to Lab format
lab_cvd = rgb_to_lab(img_cvd)

# 5) Calculate ΔE between color blindness and normal
delta = deltaE_2000(lab_normal, lab_cvd)

print("Mean DeltaE:", float(delta.mean()))
print("Max DeltaE:", float(delta.max()))
print("Min DeltaE:", float(delta.min()))
