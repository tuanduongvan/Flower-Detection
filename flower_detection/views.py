from django.shortcuts import render, redirect
from django.http import JsonResponse
import cv2
import base64, json, logging
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO

# Create your views here.
def indext(request):
    return render(request, 'homepage.html')

def scan(request):
    pass
def video_on_web(request):
    return render(request, 'Capture.html')



CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

labels = { 0 : 'hello'}

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
    boxes = get_output_tensor(interpreter, 0)
    classes = get_output_tensor(interpreter, 1)
    scores = get_output_tensor(interpreter, 2)
    count = int(get_output_tensor(interpreter, 3))

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

            interpreter = tf.lite.Interpreter(model_path='D:/test/Flower (1)/webapp/detect.tflite')
            interpreter.allocate_tensors()

            img = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            img = cv2.resize(img, (320, 320))
            res = detect_objects(interpreter, img, 0.1)
            print(res)

            for result in res:
                ymin, xmin, ymax, xmax = result['bounding_box']
                xmin = int(max(1, xmin * CAMERA_WIDTH))
                xmax = int(min(CAMERA_WIDTH, xmax * CAMERA_WIDTH))
                ymin = int(max(1, ymin * CAMERA_HEIGHT))
                ymax = int(min(CAMERA_HEIGHT, ymax * CAMERA_HEIGHT))

                confidence_score = result['score']

                cv2.rectangle(image_np, (xmin, ymin), (xmax, ymax), (0, 255, 0), 3)
                cv2.putText(image_np, f"{labels[int(result['class_id'])]}: {confidence_score:.2f}", 
                            (xmin, min(ymax, CAMERA_HEIGHT - 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)



            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', image_np)
            result_image = base64.b64encode(buffer).decode('utf-8')
            return JsonResponse({'image': result_image})

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

