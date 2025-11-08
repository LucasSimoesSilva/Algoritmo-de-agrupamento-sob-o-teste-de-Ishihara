from color_utils import *
from cluster_utils import *


def kmeans_ab(ab_samples: np.ndarray, cluster_number: int = 6, attempts: int = 5, criteria_eps: float = 0.5,
              criteria_iter: int = 50):
    """
    k-means using OpenCV on a*b*(float32).
    Returns centroids (k,2) and labels (n,).
    """

    # Points in the format (n,2)
    points = ab_samples.reshape(-1, 2)

    # Stopping criterion: when the maximum number of iterations is reached or when there is no significant improvement.
    # (criteria_type, max_iter, epsilon)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, criteria_iter, criteria_eps)

    compactness, labels, cluster_centers = cv2.kmeans(
        points, K=cluster_number, bestLabels=None, criteria=criteria,
        attempts=attempts, flags=cv2.KMEANS_PP_CENTERS
    )

    # Flatten labels to a 1D vector
    labels = labels.reshape(-1)

    # Return cluster centers and labels
    return cluster_centers.astype(np.float32), labels


def simulate_palette_cvd(centroids_lab: np.ndarray, cvd_type: str, severity: float) -> np.ndarray:
    """
    Converts palette Lab -> RGB -> simulates CVD -> converts back to Lab.
    centroids_lab: (k,3)
    Returns: (k,3) in Lab already simulated.
    """

    # shape: (k,3)
    palette_rgb = lab_to_rgb(centroids_lab)

    # Treat the palette as a 1xk "image" because simulate_cvd expects (H, W, 3)
    palette_rgb_img = palette_rgb[None, :, :]

    palette_cvd_rgb_img = simulate_cvd(palette_rgb_img, cvd_type=cvd_type, severity=severity)

    # Back to shape (k,3)
    palette_cvd_rgb = palette_cvd_rgb_img.reshape(-1, 3)

    palette_cvd_lab = color.rgb2lab(palette_cvd_rgb).astype(np.float32)
    return palette_cvd_lab


def pairwise_delta_lab(palette_lab: np.ndarray) -> np.ndarray:
    """
    Computes a ΔE2000 distance matrix between two colors from the palette_lab.
    """
    num_colors = palette_lab.shape[0]
    delta_matrix = np.zeros((num_colors, num_colors), dtype=np.float32)

    for i in range(num_colors):
        # Repeat the i-th Lab color 'num_colors' times
        color_i_repeated = np.repeat(palette_lab[i][None, :], num_colors, axis=0)

        # Compute ΔE2000 between color i and every other color
        delta_matrix[i] = deltaE_2000(color_i_repeated, palette_lab)

    return delta_matrix


def collision_graph(delta_cvd_matrix: np.ndarray, threshold: float = 8.0):
    """
    Returns list of (i, j, ΔE) pairs where ΔE under CVD < threshold.
    These represent collisions (colors too similar after simulation).
    """
    num_colors = delta_cvd_matrix.shape[0]
    collision_edges = []

    for i in range(num_colors):
        for j in range(i + 1, num_colors):
            # If two colors become perceptually too similar, record this collision
            if delta_cvd_matrix[i, j] < threshold:
                collision_edges.append((i, j, float(delta_cvd_matrix[i, j])))

    return collision_edges


def analyze_collisions(image_path: str, cluster_number: int = 6, cvd_type: str = "deutan", severity: float = 1.0,
                       threshold: float = 8.0):
    """
    Returns: (lab_centroids, lab_centroids_cvd, deltaE_matrix_cvd, collisions)
    """

    # 1) Read image and convert to Lab
    img_rgb = read_rgb(image_path)
    img_lab = rgb_to_lab(img_rgb)

    # 2) Sample a*b* points and run k-means on chroma only
    ab_samples, sample_rows, sample_cols = sample_ab_from_lab(img_lab, max_samples=50_000)
    ab_centers, cluster_labels = kmeans_ab(ab_samples, cluster_number=cluster_number)

    # 3) Build full Lab centroids
    lab_centroids = build_lab_centroids(
        img_lab, cluster_labels, sample_rows, sample_cols, ab_centers
    )

    # 4) Simulate CVD on centroids and compute pairwise ΔE between simulated centroids
    lab_centroids_cvd = simulate_palette_cvd(lab_centroids, cvd_type=cvd_type, severity=severity)
    delta_matrix_cvd = pairwise_delta_lab(lab_centroids_cvd)

    # 5) Collisions (ΔE < threshold)
    collisions = collision_graph(delta_matrix_cvd, threshold=threshold)

    # 6) Print
    print(f"Clusters: {cluster_number}, CVD: {cvd_type}, severity: {severity}, threshold: {threshold}")
    print("ΔE2000 matrix under CVD (approx.):")
    np.set_printoptions(precision=2, suppress=True)
    print(delta_matrix_cvd)

    if collisions:
        print("\nCollisions detected (i, j, ΔE):")
        for i, j, d in collisions:
            print(f"  {i} -- {j}  ΔE={d:.2f}")
    else:
        print("\nNo collisions below the threshold.")

    return lab_centroids, lab_centroids_cvd, delta_matrix_cvd, collisions
