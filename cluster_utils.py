import numpy as np

def sample_ab_from_lab(img_lab: np.ndarray, max_samples: int = 50_000, seed: int = 42):
    """
    Returns samples of a*b* and the chosen indices (sample_rows,sample_cols).

    It does not use L* (luminosity).
    """
    height, width, _ = img_lab.shape
    rng = np.random.default_rng(seed)
    total_pixels = height * width
    num_samples = min(max_samples, total_pixels)

    # Choose the indexes (0 to total_pixels-1) without repetition
    flat_indices = rng.choice(total_pixels, size=num_samples, replace=False)

    sample_rows = flat_indices // width
    sample_cols = flat_indices % width

    # 'a' and 'b' are the main color properties of a pixel
    ab_samples = img_lab[sample_rows, sample_cols, 1:3].astype(np.float32)
    return ab_samples, sample_rows, sample_cols


def build_lab_centroids(img_lab: np.ndarray, cluster_labels: np.ndarray, sample_rows: np.ndarray,
                        sample_cols: np.ndarray, ab_centers: np.ndarray) -> np.ndarray:
    """
    For each cluster, defines an L* and create the LAB cluster centers
    """

    num_clusters = ab_centers.shape[0]

    # Get L* from each pixel
    l_samples = img_lab[sample_rows, sample_cols, 0].astype(np.float32)

    # Start LAB array
    lab_centroids = np.zeros((num_clusters, 3), dtype=np.float32)

    for i in range(num_clusters):
        in_cluster = (cluster_labels == i)

        if not np.any(in_cluster):
            # If cluster is empty, uses global median L*
            l_repr = float(np.median(img_lab[..., 0]))
        else:
            # L* median from cluster
            l_repr = float(np.median(l_samples[in_cluster]))

        # Put L* in the right array (a*, b*)
        lab_centroids[i] = np.array(
            [l_repr, ab_centers[i, 0], ab_centers[i, 1]],
            dtype=np.float32
        )

    return lab_centroids