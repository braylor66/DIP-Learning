import gradio as gr
import cv2
import numpy as np

def apply_transform(image, scale, rotation, translation_x, translation_y, flip_horizontal):
    image = np.array(image)
    border_size = 500 
    padded_image = cv2.copyMakeBorder(
        image, border_size, border_size, border_size, border_size, 
        cv2.BORDER_CONSTANT, value=[222, 253, 255]
    )
    h, w = image.shape[:2]
    center = (w // 2 + border_size, h // 2 + border_size)  # Center of the actual image
    
    transform_matrix = cv2.getRotationMatrix2D(center, rotation, scale)
   
    transform_matrix[0, 2] += translation_x
    transform_matrix[1, 2] += translation_y
    
    transformed_image = cv2.warpAffine(
        padded_image, transform_matrix, 
        (padded_image.shape[1], padded_image.shape[0]), 
        borderValue=(255, 255, 255)
    )
    
    if flip_horizontal:
        transformed_image = cv2.flip(transformed_image, 1)
    
    return transformed_image

def interactive_transform():
    with gr.Blocks(css=".gradio-container {width: 800px; margin: auto;}") as demo:
        gr.Markdown("## Image Transformation Playground")
        
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Upload Image")

                scale = gr.Slider(minimum=0.1, maximum=2.0, step=0.1, value=1.0, label="Scale")
                rotation = gr.Slider(minimum=-180, maximum=180, step=1, value=0, label="Rotation (degrees)")
                translation_x = gr.Slider(minimum=-300, maximum=300, step=10, value=0, label="Translation X")
                translation_y = gr.Slider(minimum=-300, maximum=300, step=10, value=0, label="Translation Y")
                flip_horizontal = gr.Checkbox(label="Flip Horizontal")
            
            image_output = gr.Image(label="Transformed Image")
        
        inputs = [
            image_input, scale, rotation, 
            translation_x, translation_y, 
            flip_horizontal
        ]

        image_input.change(apply_transform, inputs, image_output)
        scale.change(apply_transform, inputs, image_output)
        rotation.change(apply_transform, inputs, image_output)
        translation_x.change(apply_transform, inputs, image_output)
        translation_y.change(apply_transform, inputs, image_output)
        flip_horizontal.change(apply_transform, inputs, image_output)

    return demo

interactive_transform().launch()
