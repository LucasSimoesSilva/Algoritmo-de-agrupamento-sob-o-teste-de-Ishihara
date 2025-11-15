from cluster_cvd_step import *

(lab_centroids, lab_centroids_cvd, delta_cvd, collisions,
 centroids_optimized, palette_cvd_lab_optimized,
 delta_cvd_optimized, collisions_optimized) = analyze_collisions(
    "../images/ishiharaTest.png", cluster_number=6, cvd_type="deutan", severity=1.0, threshold=8.0
)
