import cv2
import numpy as np
import gradio as gr

# 初始化全局变量，存储控制点和目标点
points_src = []
points_dst = []
image = None

# 上传图像时清空控制点和目标点
def upload_image(img):
    global image, points_src, points_dst
    points_src.clear()  # 清空控制点
    points_dst.clear()  # 清空目标点
    image = img
    return img

# 记录点击点事件，并标记点在图像上，同时在成对的点间画箭头
def record_points(evt: gr.SelectData):
    global points_src, points_dst, image
    x, y = evt.index[0], evt.index[1]  # 获取点击的坐标
    
    # 判断奇偶次来分别记录控制点和目标点
    if len(points_src) == len(points_dst):
        points_src.append([x, y])  # 奇数次点击为控制点
    else:
        points_dst.append([x, y])  # 偶数次点击为目标点
    
    # 在图像上标记点（蓝色：控制点，红色：目标点），并画箭头
    marked_image = image.copy()
    for pt in points_src:
        cv2.circle(marked_image, tuple(pt), 1, (255, 0, 0), -1)  # 蓝色表示控制点
    for pt in points_dst:
        cv2.circle(marked_image, tuple(pt), 1, (0, 0, 255), -1)  # 红色表示目标点
    
    # 画出箭头，表示从控制点到目标点的映射
    for i in range(min(len(points_src), len(points_dst))):
        cv2.arrowedLine(marked_image, tuple(points_src[i]), tuple(points_dst[i]), (0, 255, 0), 1)  # 绿色箭头表示映射
    
    return marked_image

# 执行仿射变换




def point_guided_deformation(image, source_pts,target_pts,  alpha=1.0, eps=1e-8):
    h, w = image.shape[:2]
    deformed_image = np.zeros_like(image)
    
    
    for x in range(w):
        for y in range(h):
            p = np.array([x, y])
            weights = np.array([1 / (np.linalg.norm(p - q) ** (alpha*2) + eps) for q in target_pts])
            weighted_source = np.sum(weights[:, None] * target_pts, axis=0)
            weighted_target = np.sum(weights[:, None] * source_pts, axis=0)
            new_target_pts = target_pts - np.tile(weighted_source, (target_pts.shape[0], 1))
            new_source_pts = source_pts - np.tile(weighted_target, (source_pts.shape[0], 1))
            result1 = np.linalg.inv(np.sum([w * np.outer(A_i, A_i) for A_i, w in zip(new_target_pts, weights)], axis=0))
            result2 = np.sum([w * np.outer(A_i, B_i) for A_i,B_i, w in zip(new_target_pts,new_source_pts, weights)], axis=0)
            try:
                transformed_p = np.round(np.dot(np.dot(p - weighted_source, result1), result2) + weighted_target).astype(int)
            except Exception as e:
                print(f"An error occurred: {e}")
                print("weighted_source:", weighted_source)
                print("p:", p)
                print("result1:", result1)
                print("result2:", result2)
            x_int = np.clip(transformed_p[0], 0, image.shape[1] - 1)
            y_int = np.clip(transformed_p[1], 0, image.shape[0] - 1)
            deformed_image[y, x] = image[y_int, x_int]
    return deformed_image


def run_warping():
    global points_src, points_dst, image ### fetch global variables

    warped_image = point_guided_deformation(image, np.array(points_src), np.array(points_dst))

    return warped_image

# 清除选中点
def clear_points():
    global points_src, points_dst
    points_src.clear()
    points_dst.clear()
    return image  # 返回未标记的原图

# 使用 Gradio 构建界面
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(source="upload", label="上传图片", interactive=True, width=800, height=200)
            point_select = gr.Image(label="点击选择控制点和目标点", interactive=True, width=800, height=800)
            
        with gr.Column():
            result_image = gr.Image(label="变换结果", width=800, height=400)
    
    run_button = gr.Button("Run Warping")
    clear_button = gr.Button("Clear Points") 
    
    input_image.upload(upload_image, input_image, point_select)
    point_select.select(record_points, None, point_select)
    run_button.click(run_warping, None, result_image)
    clear_button.click(clear_points, None, point_select)
    
demo.launch()
