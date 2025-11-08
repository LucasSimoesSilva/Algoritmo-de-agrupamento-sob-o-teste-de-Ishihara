from color_utils import *

img_ishihara = read_rgb("../images/ishiharaTest.png")
img_red = read_rgb("../images/vermelho.png")

simulation_ishihara = simulate_cvd(img_ishihara, cvd_type="deutan", severity=0.8)
simulation_red = simulate_cvd(img_red, cvd_type="deutan", severity=0.8)

write_rgb("../images/saida_deutan_ishihara.png", simulation_ishihara)
write_rgb("../images/saida_deutan_red.png", simulation_red)
