import requests
from io import BytesIO
from PIL import Image
from firebase import upload_to_firebase
from datetime import datetime
import cv2
import numpy as np
import os
import shutil

def extract_characters(image_path, character_name, output_dir, name, studentTaskId, min_contour_area=3500, aspect_ratio_threshold=0.3):
    # 이미지 읽기
    # 이미지 다운로드
    pil_image = download_image(image_path)
    
    # PIL 이미지를 OpenCV 형식으로 변환
    image  = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)   

    # 투명 채널이 있을 경우 분리
    if image.shape[2] == 4:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.addWeighted(gray, 0.5, alpha, 0.5, 0)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 적응형 임계값 처리
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # 모폴로지 연산 (약화된 형태)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # 외곽선 검출
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    extracted_images = []
    counter = 1  # 파일 이름에 붙일 숫자를 저장할 변수
    
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:  # 작은 컨투어 무시
            # 윤곽선 경계 상자 계산
            x, y, w, h = cv2.boundingRect(contour)
            
            # 가로세로 비율로 필터링 (너무 길거나 좁은 윤곽선 제거)
            aspect_ratio = float(w) / h
            if aspect_ratio < aspect_ratio_threshold or aspect_ratio > (1 / aspect_ratio_threshold):
                continue
            
            # 각 캐릭터 추출
            character = image[y:y+h, x:x+w]
            
            # 배경을 투명하게 하기 위해 알파 채널 추가
            if character.shape[2] == 3:  # RGB일 경우
                character_alpha = np.zeros((h, w, 4), dtype=np.uint8)
                character_alpha[:, :, :3] = character
            else:  # RGBA일 경우
                character_alpha = character
            
            # 마스크 생성
            mask = np.zeros((h, w), dtype=np.uint8)
            mask = cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1, offset=(-x, -y))
            character_alpha[:, :, 3] = mask
            
            # 캐릭터 주변의 픽셀을 좀 더 깔끔하게 다듬기 위해 윤곽선 확장 (팽창 연산)
            kernel_dilate = np.ones((3, 3), np.uint8)
            character_alpha[:, :, 3] = cv2.dilate(character_alpha[:, :, 3], kernel_dilate, iterations=1)
            
            # 이미지 저장
            output_path = os.path.join(output_dir, f"{character_name}_{counter}.png")
            extracted_images.append(output_path)
            cv2.imwrite(output_path, character_alpha)
            
            counter += 1  # 숫자 증가

    result_image_arr = []

    for i, output_path in enumerate(extracted_images):

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        name_with_time = f"{studentTaskId}_{name}_{current_time}"
        
        destination_blob_name = f"image/{studentTaskId}/{name}/{name_with_time}_{i}.png"


        public_url = upload_to_firebase(output_path, destination_blob_name)
        result_image_arr.append(public_url)
    
    return result_image_arr

# URL에서 이미지 다운로드
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    else:
        raise Exception("Failed to download image")

def process_and_upload_images(data):

    # # 이미지 폴더 비우기
    # images_folder = 'images'
    # if os.path.exists(images_folder):
    #     shutil.rmtree(images_folder)
    
    # os.makedirs(images_folder, exist_ok=True)

    studentTaskId = data['studentTaskId']
    characters = data['characters']
    result = []
    
    for i, character in enumerate(characters):

        name = character['name']
        imageUrl = character['imageUrl']

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        name_with_time = f"{studentTaskId}_{name}_{current_time}"

        output_dir = f'images/{name_with_time}/'

        os.makedirs(output_dir, exist_ok=True)

        result_image_arr = extract_characters(imageUrl, name, output_dir, name, studentTaskId)

        result.append({name: result_image_arr})
    
    return result
