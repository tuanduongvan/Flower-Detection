from django.shortcuts import render, redirect
from django.http import JsonResponse
import cv2
import re
import base64, json, logging
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
from .models import Flower, SearchHistory
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404

# Create your views here.
def indext(request):
    return render(request, 'homepage.html')

def scan(request):
    pass
def video_on_web(request):
    return render(request, 'Capture.html')



CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

finalhistory = SearchHistory()

def load_labels(path):
    """Loads the labels file. Supports files with or without index numbers."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for row_number, content in enumerate(lines):
            content = content.strip()
            if content:
                labels[row_number] = content
    return labels

# labels = {0: 'hoa su', 1: 'hoa hong', 2: 'van tho', 3: 'hoa dam but', 4: 'hoa sen', 5: 'hoa giay'}

def set_input_tensor(interpreter, image):
    """Sets the input tensor."""
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = np.expand_dims((image - 255) / 255, axis=0)

def get_output_tensor(interpreter, index):
    output_details = interpreter.get_output_details()[index] # lay gia tri tai index trong ket qua tra ve cua get_ouput_details [boundingbox, class, score, count]
    tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
    return tensor

def detect_objects(interpreter, image, threshold):
    """Returns a list of detection results, each a dictionary of object info."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    # Get all output details
    scores = get_output_tensor(interpreter, 0)
    count = int(get_output_tensor(interpreter, 2))
    boxes = get_output_tensor(interpreter, 1)
    classes = get_output_tensor(interpreter, 3)

    results = []
    for i in range(count):
        if scores[i] >= threshold:
            result = {
                'bounding_box': boxes[i],
                'class_id': int(classes[i]),
                'score': float(scores[i])
            }
            results.append(result)
    return results

def main(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            base64_image = json_data['image']
            image_data = base64.b64decode(base64_image)  # giải mã ảnh base64 thành dữ liệu nhị phân
            image = Image.open(BytesIO(image_data))

            image_np = np.array(image)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                image_np = np.array(image)

            # interpreter = tf.lite.Interpreter(model_path='C:\\Users\\PC\Desktop\\AI project\\PBL4_flower\\Flower-Detection\\detect.tflite')
            interpreter = tf.lite.Interpreter(model_path='D:/test/Flower (1)/webapp/detect.tflite')
            interpreter.allocate_tensors()

            img = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            img = cv2.resize(img, (320, 320))
            res = detect_objects(interpreter, img, 0.5)
            print(res)

            CAMERA_WIDTH = image_np.shape[1]
            CAMERA_HEIGHT = image_np.shape[0]

            # Danh sách các kết quả để gửi về client
            results_list = []

            labels = load_labels('labels.txt')
            print(labels)

            # Tạo dictionary để lưu giữ kết quả tốt nhất cho mỗi class_id
            best_results = {}

            # Lọc các kết quả có score cao nhất cho mỗi class_id
            for result in res:
                class_id = result['class_id']
                if class_id not in best_results or result['score'] > best_results[class_id]['score']:
                    best_results[class_id] = result

            # Chuyển dictionary thành danh sách kết quả đã lọc
            filtered_res = list(best_results.values())
            print(filtered_res)

            for result in filtered_res:
                ymin, xmin, ymax, xmax = result['bounding_box']
                xmin = int(max(1, xmin * CAMERA_WIDTH))
                xmax = int(min(CAMERA_WIDTH, xmax * CAMERA_WIDTH))
                ymin = int(max(1, ymin * CAMERA_HEIGHT))
                ymax = int(min(CAMERA_HEIGHT, ymax * CAMERA_HEIGHT))

                confidence_score = result['score']

                # Vẽ bounding box và label lên ảnh
                cv2.rectangle(image_np, (xmin, ymin), (xmax, ymax), (0, 255, 0), 3)
                cv2.putText(image_np, f"{labels[int(result['class_id'])]}: {confidence_score:.2f}", 
                            (xmin, min(ymax, CAMERA_HEIGHT - 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Thêm thông tin thẻ a vào kết quả
                results_list.append({
                    'label': labels[int(result['class_id'])],
                    'score': confidence_score,
                    'link': f"/flower/{int(result['class_id'])}"
                })

            # Mã hóa ảnh trả về
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', image_np)
            result_image = base64.b64encode(buffer).decode('utf-8')

            label = load_labels('label1.txt')

            if(filtered_res):
                link_flower = ''
                for result in filtered_res:
                    link = f'<a href="/flower/{int(result["class_id"])}"  class="info-button" > {label[int(result["class_id"])]} </a>'
                    link_flower += link
                history = SearchHistory(
                    linkflower = link_flower,
                    image = result_image,
                    time = now() 
                )
                global finalhistory
                finalhistory.define(history)

            # Trả về ảnh và danh sách các thẻ a
            return JsonResponse({
                'image': result_image,
                'results': results_list
            })

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def flower_detail(request, id):
    flower = get_object_or_404(Flower, id=id)
    finalhistory.save()
    return render(request, 'flower_detail.html', {'flower': flower})

def History(request):
    list_history = SearchHistory.objects.all().order_by('-id')
    return render(request, 'histori.html', {'list_history': list_history})