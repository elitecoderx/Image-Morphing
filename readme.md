# Image Morphing App

## Overview
The **Image Morphing App** is a Python-based web application that allows users to morph one image into another using feature-based interpolation techniques. The app supports manual selection of feature points, Delaunay triangulation, and smooth transition rendering with barycentric interpolation.

<p align="center">
  <img src="morphing.gif" alt="Image Morphing Example" width="200">
</p>

## Live Demo:
[Click here to try now](https://elitecoderx.streamlit.app/) 🚀  

## Features
- **Image Normalization**: Resizes images to match dimensions.
- **Feature Point Selection**: Users can manually specify corresponding points.
- **Delaunay Triangulation**: Creates a structured mesh for interpolation.
- **Intermediate Frame Generation**: Interpolates feature points and applies smooth transitions.
- **Barycentric Interpolation**: Computes pixel values for seamless morphing.
- **GIF Export**: Generates and exports a morphing animation.

- **Interactive UI**: Enhanced visualization and real-time feedback with progress tracking.

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed.

### Setup Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/elitecoderx/Image-Morphing.git
   cd Image-Morphing
   ```
2. Install pipenv for virtual environment:
   ```sh
   pip install pipenv
   ```
3. Install dependencies and and activate it:
   ```sh
   pipenv install
   pipenv shell
   ```
4. Run the Streamlit app:
   ```sh
   streamlit run app.py
   ```

## Usage
1. Upload source and target images.
2. Select corresponding feature points.
3. Perform Delaunay triangulation.
4. Generate and preview intermediate frames.
5. Save the morphing sequence as a GIF.

## Future Enhancements
- **Automated Feature Detection** using deep learning.
- **User Customization** for interpolation parameters.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

