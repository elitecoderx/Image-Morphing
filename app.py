import pandas as pd
import streamlit as st
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from helpers import draw_points, interpolate_points, render_triangle


# --- Session State Initialization ---
if "points" not in st.session_state:
    st.session_state["points"] = pd.DataFrame(
        {"Source X": [], "Source Y": [], "Target X": [], "Target Y": []}
    )

if "success" not in st.session_state:
    st.session_state.success = {"step1": False, "step2": False, "step3": False}

if "images" not in st.session_state:
    st.session_state.images = {"source": None, "target": None}

st.set_page_config(
    page_title="elitecoderX - Image Morpher",
    initial_sidebar_state="collapsed",
    layout="centered",
)

# --- Title ---
st.title("🌠 :rainbow[Image Morphing App]")

# --- Image Upload ---
col1, col2 = st.columns(2)
with col1:
    source_file = st.file_uploader(":red[Upload Source Image:]", type=["jpg", "png"])
    if source_file:
        st.success("Source Image uploaded successfully.", icon="✅")

with col2:
    target_file = st.file_uploader(":red[Upload Target Image:]", type=["jpg", "png"])
    if target_file:
        st.success("Target Image uploaded successfully.", icon="✅")

# --- Step 1: Normalize Images ---
if source_file and target_file:
    st.header("🌃 Normalize Images")
    w = st.slider(
        ":red[Width:]",
        min_value=100,
        max_value=500,
        value=300,
        step=10,
        key="width_input",
    )
    h = st.slider(
        ":red[Height:]",
        min_value=100,
        max_value=500,
        value=300,
        step=10,
        key="height_input",
    )

    if st.button("Normalize Images", use_container_width=True):
        st.session_state.images["source"] = (
            Image.open(source_file).resize((w, h)).convert("RGB")
        )
        st.session_state.images["target"] = (
            Image.open(target_file).resize((w, h)).convert("RGB")
        )
        st.session_state.success["step1"] = True
    if st.session_state.success["step1"]:
        st.success("Images normalized successfully!", icon="✅")

# --- Step 2: Select Corresponding Points ---
if st.session_state.success["step1"]:
    st.header("✨ Select Corresponding Points")
    col1, col2 = st.columns(2)

    # Handle source point selection
    with col1:
        st.subheader(":red[Source Image]")
        if st.session_state.images["source"]:
            source_image = st.session_state.images["source"].copy()
            source_image = draw_points(
                source_image,
                st.session_state.points["Source X"],
                st.session_state.points["Source Y"],
            )
            value = streamlit_image_coordinates(source_image, use_column_width=True)
            if value:
                new_x = round(value["x"] / value["width"] * w)
                new_y = round(value["y"] / value["height"] * h)
                # Add point to dataframe
                st.session_state.points.loc[len(st.session_state.points)] = {
                    "Source X": new_x,
                    "Source Y": new_y,
                    "Target X": None,
                    "Target Y": None,
                }
                st.rerun()

    # Handle target point selection
    with col2:
        st.subheader(":red[Target Image]")
        if st.session_state.images["target"]:
            target_image = st.session_state.images["target"].copy()
            target_image = draw_points(
                target_image,
                st.session_state.points["Target X"],
                st.session_state.points["Target Y"],
            )
            value = streamlit_image_coordinates(target_image, use_column_width=True)
            if value:
                if st.session_state.points[
                    st.session_state.points["Target X"].isna()
                ].empty:
                    st.toast(
                        "Please select a corresponding point in the source image first.",
                        icon="⚠️",
                    )
                else:
                    new_x = round(value["x"] / value["width"] * w)
                    new_y = round(value["y"] / value["height"] * h)
                    # Update the latest row where the target point is missing
                    last_idx = st.session_state.points[
                        st.session_state.points["Target X"].isna()
                    ].index[0]
                    st.session_state.points.at[last_idx, "Target X"] = new_x
                    st.session_state.points.at[last_idx, "Target Y"] = new_y
                    st.rerun()

    # --- Display Points in Tabular Format ---
    st.subheader("📅 Selected Points")

    # Add corner points if not already added
    corner_points = [(0, 0), (0, h), (w, 0), (w, h)]
    for sx, sy in corner_points:
        if not (
            (st.session_state.points["Source X"] == sx)
            & (st.session_state.points["Source Y"] == sy)
        ).any():
            st.session_state.points.loc[len(st.session_state.points)] = {
                "Source X": sx,
                "Source Y": sy,
                "Target X": sx,
                "Target Y": sy,
            }

    st.session_state.points = st.data_editor(
        st.session_state.points, num_rows="dynamic", hide_index=False
    )
    col1, col2 = st.columns(2)

    if col1.button("Reset Points", use_container_width=True):
        st.session_state.pop("points")
        st.rerun()

    if col2.button("Save Points", use_container_width=True):
        st.session_state.success["step2"] = True
    if st.session_state.success["step2"]:
        st.success("All points saved successfully!", icon="✅")

# --- Step 3: Perform Delaunay Triangulation ---
if st.session_state.success["step2"]:
    st.header("🎆 Delaunay Triangulation")

    # Extract source and target points
    source_points = st.session_state.points[["Source X", "Source Y"]].dropna().values
    target_points = st.session_state.points[["Target X", "Target Y"]].dropna().values

    if len(source_points) >= 3:
        if len(target_points) != len(source_points):
            st.warning(
                "Please ensure all source points have corresponding target points."
            )
        else:
            tri = Delaunay(source_points)
            col1, col2 = st.columns(2)
            with col1:
                # Display triangles on source image
                source_img = st.session_state.images["source"].copy()
                draw = ImageDraw.Draw(source_img)
                for simplex in tri.simplices:
                    pts = [tuple(source_points[i]) for i in simplex]
                    draw.polygon(pts, outline="blue", width=1)
                st.image(source_img, caption="Source Image with Triangulation")

            with col2:
                # Display corresponding triangles on target image
                target_img = st.session_state.images["target"].copy()
                draw = ImageDraw.Draw(target_img)
                for simplex in tri.simplices:
                    if max(simplex) >= len(target_points):
                        continue
                    pts = [tuple(target_points[i]) for i in simplex]
                    draw.polygon(pts, outline="blue", width=1)
                st.image(target_img, caption="Target Image with Mapped Triangulation")
                st.session_state.success["step3"] = True
    else:
        st.toast(
            "At least 3 corresponding points are required for triangulation.", icon="⚠️"
        )

# --- Step 4: Generate Morphing GIF ---
if st.session_state.success["step3"]:
    st.header("🎁 Morphing GIF Generation")
    n = st.slider(":red[Intermediate Images:]", min_value=1, max_value=10, value=5)

    source_points = st.session_state.points[["Source X", "Source Y"]].dropna().values
    target_points = st.session_state.points[["Target X", "Target Y"]].dropna().values

    source_img = st.session_state.images["source"]
    target_img = st.session_state.images["target"]

    source_tri = Delaunay(source_points)

    if st.button("✨ Generate", use_container_width=True):
        gif_path = "morphing.gif"
        progress_bar = st.progress(0)
        status_text = st.empty()

        w, h = source_img.size
        frames = [source_img]

        emojis = [
            "🚀",
            "⚡",
            "🌌",
            "🌀",
            "🌟",
            "💡",
            "🎨",
            "🔬",
            "🛠️",
            "🎭",
            "🧩",
            "🧨",
            "🎶",
            "🕹️",
            "📡",
            "🔧",
            "🌍",
            "🧬",
            "✨",
            "🤖",
        ]

        frame_paths = []  # Store individual frame paths for download

        for i in range(1, n + 1):
            t = i / (n + 1)
            interpolated_points = interpolate_points(source_points, target_points, t)

            intermediate_img = Image.new("RGB", (w, h), "white")
            for simplex in source_tri.simplices:
                render_triangle(
                    intermediate_img,
                    source_img,
                    target_img,
                    simplex,
                    source_points,
                    target_points,
                    interpolated_points,
                    t,
                )

            frames.append(intermediate_img)

            # Save individual frames
            frame_path = f"frame_{i}.png"
            intermediate_img.save(frame_path)
            frame_paths.append(frame_path)

            progress = int((i / n) * 100)
            progress_bar.progress(progress)
            status_text.text(
                f"{emojis[i % len(emojis)]} Generating frame {i} of {n}... ({progress}%)"
            )

        frames.append(target_img)
        frames[0].save(
            gif_path, save_all=True, append_images=frames[1:], duration=200, loop=0
        )

        progress_bar.progress(100)
        status_text.text("🎊 Morphing Complete!")
        st.balloons()
        st.session_state["generated_gif"] = gif_path
        st.session_state["frame_paths"] = frame_paths

    # Display the generated GIF
    if "generated_gif" in st.session_state:
        gif_path = st.session_state["generated_gif"]
        frame_paths = st.session_state.get("frame_paths", [])

        st.markdown("## 🎭 Morphing Result")
        st.image(gif_path, use_container_width=True)

        # Download buttons
        with open(gif_path, "rb") as file:
            st.download_button(
                label="🪄 :rainbow[Download GIF]",
                data=file,
                file_name="morphing.gif",
                mime="image/gif",
                use_container_width=True,
            )

        # Allow users to download specific frames
        with st.expander("📸 Download Individual Frames"):
            cols = st.columns(5)
            for i, frame_path in enumerate(frame_paths):
                with cols[i % 5]:
                    st.image(
                        frame_path, caption=f"Frame {i+1}", use_container_width=True
                    )
                    with open(frame_path, "rb") as f:
                        st.download_button(
                            label=f":rainbow[Download]",
                            data=f,
                            file_name=frame_path,
                            mime="image/png",
                            use_container_width=True,
                        )
