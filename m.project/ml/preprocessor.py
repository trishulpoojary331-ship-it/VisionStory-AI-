import os
import cv2
import numpy as np
from PIL import Image

try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    transforms = None
    TORCH_AVAILABLE = False


class ImagePreprocessor:
    """
    Image Preprocessing Pipeline using OpenCV, PIL, and PyTorch Torchvision.
    Performs format validation, noise check, Laplacian sharpness calculation,
    dominant color extraction, and PyTorch tensor normalization (ImageNet standards).
    """

    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        
        if TORCH_AVAILABLE and transforms is not None:
            # PyTorch Vision Preprocessing Transform Pipeline
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.CenterCrop(self.target_size),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            self.transform = None

    def preprocess(self, image_path):
        """
        Complete preprocessing pipeline on an image file.
        Returns processed tensor (or array) and detailed preprocessing diagnostic metrics.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        # 1. Open with PIL for RGB fidelity
        pil_img = Image.open(image_path).convert("RGB")
        orig_w, orig_h = pil_img.size

        # 2. OpenCV operations for quality analysis
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            # Fallback if cv2 fails on certain unicode paths
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # 3. Quality Diagnostics
        # Laplacian variance measures blurriness/sharpness
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_rating = "Crisp / High Detail" if laplacian_var > 150 else ("Acceptable" if laplacian_var > 50 else "Soft / Slight Blur")

        # Brightness & Contrast
        mean_brightness = float(np.mean(gray))
        contrast_std = float(np.std(gray))
        
        if mean_brightness < 60:
            lighting_category = "Nocturnal / Low-Light"
        elif mean_brightness > 190:
            lighting_category = "High-Key / Overexposed"
        else:
            lighting_category = "Balanced Natural Light"

        # Dominant Colors & Palette
        dominant_colors = self._extract_dominant_colors(pil_img)
        color_temp = self._estimate_color_temperature(dominant_colors)

        # 4. PyTorch Preprocessing Tensor
        tensor = None
        tensor_stats = {}
        if TORCH_AVAILABLE and self.transform is not None:
            raw_tensor = self.transform(pil_img)
            if hasattr(raw_tensor, 'unsqueeze'):
                tensor = raw_tensor.unsqueeze(0)
                tensor_stats = {
                    "shape": list(tensor.shape),
                    "dtype": str(tensor.dtype),
                    "min_val": round(float(tensor.min()), 3),
                    "max_val": round(float(tensor.max()), 3),
                    "mean_val": round(float(tensor.mean()), 3),
                    "device": "CPU"
                }
        else:
            # Fallback normalized array
            resized = pil_img.resize(self.target_size)
            arr = np.array(resized, dtype=np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            arr = (arr - mean) / std
            arr = np.transpose(arr, (2, 0, 1))
            tensor_stats = {
                "shape": [1, 3, 224, 224],
                "dtype": "float32 (NumPy fallback)",
                "min_val": round(float(arr.min()), 3),
                "max_val": round(float(arr.max()), 3),
                "mean_val": round(float(arr.mean()), 3),
                "device": "CPU"
            }

        diagnostics = {
            "original_dimensions": {"width": orig_w, "height": orig_h},
            "aspect_ratio": round(orig_w / max(1, orig_h), 2),
            "sharpness": {
                "laplacian_variance": round(laplacian_var, 1),
                "assessment": sharpness_rating
            },
            "lighting": {
                "mean_brightness": round(mean_brightness, 1),
                "contrast_level": round(contrast_std, 1),
                "category": lighting_category,
                "color_temperature": color_temp
            },
            "dominant_colors": dominant_colors,
            "pytorch_tensor": tensor_stats
        }

        return tensor, diagnostics, pil_img

    def _extract_dominant_colors(self, pil_img, num_colors=4):
        """Extract top dominant hex colors from image thumbnail using k-means/quantization."""
        thumb = pil_img.copy()
        thumb.thumbnail((100, 100))
        # Quantize to reduce color space
        quantized = thumb.quantize(colors=num_colors)
        palette = quantized.getpalette()[:num_colors * 3]
        
        colors = []
        for i in range(num_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            colors.append({"r": r, "g": g, "b": b, "hex": hex_code})
        return colors

    def _estimate_color_temperature(self, dominant_colors):
        """Estimate whether palette is Warm, Golden, Cool, or Neutral."""
        if not dominant_colors:
            return "Neutral"
        
        warm_weight = 0
        cool_weight = 0
        for c in dominant_colors:
            r, g, b = c["r"], c["g"], c["b"]
            if r > b + 20:
                warm_weight += (r - b)
            elif b > r + 20:
                cool_weight += (b - r)

        if warm_weight > cool_weight + 50:
            return "Warm Sunset / Golden Amber"
        elif cool_weight > warm_weight + 50:
            return "Cool Azure / Twilight Mood"
        else:
            return "Vibrant Balanced Palette"
