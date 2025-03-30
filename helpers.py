import numpy as np
import pandas as pd
from PIL import ImageDraw, ImageFont


def get_ellipse_coords(point, radius):
    return (point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius)


def draw_points(image, x_coords, y_coords):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(image.size[0] // 30)  # Use default font

    for idx, (x, y) in enumerate(zip(x_coords, y_coords)):
        if pd.isna(x) or pd.isna(y):
            continue  # Skip if coordinates are NaN

        coords = get_ellipse_coords((int(x), int(y)), radius=image.size[0] // 100)
        draw.ellipse(coords, fill="red", outline="black")
        draw.text((int(x), int(y)), str(idx), fill="black", font=font)

    return image


def interpolate_points(source_points, target_points, t):
    """Interpolate feature points for the intermediate image."""
    return (1 - t) * np.array(source_points) + t * np.array(target_points)


def compute_barycentric_coords(p, a, b, c):
    """Compute barycentric coordinates of point p with respect to triangle (a, b, c)."""
    det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if det == 0:
        return -1, -1, -1
    u = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / det
    v = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / det
    w = 1 - u - v
    return u, v, w


def render_triangle(
    img, source_img, target_img, triangle_indices, source_pts, target_pts, interp_pts, t
):
    """Render a triangle using barycentric coordinates."""
    src_tri = [source_pts[i] for i in triangle_indices]
    tgt_tri = [target_pts[i] for i in triangle_indices]
    interp_tri = [interp_pts[i] for i in triangle_indices]

    xmin = max(int(min(p[0] for p in interp_tri)), 0)
    xmax = min(int(max(p[0] for p in interp_tri)), img.width - 1)
    ymin = max(int(min(p[1] for p in interp_tri)), 0)
    ymax = min(int(max(p[1] for p in interp_tri)), img.height - 1)

    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            u, v, w = compute_barycentric_coords((x, y), *interp_tri)
            if u < 0 or v < 0 or w < 0:
                continue

            src_x = np.clip(
                int(u * src_tri[0][0] + v * src_tri[1][0] + w * src_tri[2][0]),
                0,
                source_img.width - 1,
            )
            src_y = np.clip(
                int(u * src_tri[0][1] + v * src_tri[1][1] + w * src_tri[2][1]),
                0,
                source_img.height - 1,
            )
            tgt_x = np.clip(
                int(u * tgt_tri[0][0] + v * tgt_tri[1][0] + w * tgt_tri[2][0]),
                0,
                target_img.width - 1,
            )
            tgt_y = np.clip(
                int(u * tgt_tri[0][1] + v * tgt_tri[1][1] + w * tgt_tri[2][1]),
                0,
                target_img.height - 1,
            )

            color_s = np.array(source_img.getpixel((src_x, src_y))[:3])
            color_t = np.array(target_img.getpixel((tgt_x, tgt_y))[:3])
            color = ((1 - t) * color_s + t * color_t).astype(np.uint8)

            img.putpixel((x, y), tuple(color))