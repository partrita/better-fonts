from PIL import Image, ImageDraw, ImageFont
import os

def create_text_image(text, font_path, font_size, output_filename):
    """
    주어진 텍스트를 이미지로 생성합니다.

    Args:
        text (str): 이미지로 변환할 텍스트.
        font_path (str): 사용할 .ttf 폰트 파일의 경로.
        font_size (int): 폰트 크기.
        output_filename (str): 생성될 이미지 파일의 이름.
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error: Font file not found or could not be opened at {font_path}")
        return

    # 텍스트 크기 계산
    # Pillow 9.0.0+ 에서는 textsize 대신 textbbox를 사용합니다.
    # textbbox는 (left, top, right, bottom) 튜플을 반환합니다.
    # 시작점을 (0,0)으로 가정하여 너비와 높이를 계산합니다.
    left, top, right, bottom = ImageDraw.Draw(Image.new('RGB', (1,1))).textbbox((0,0), text, font=font)
    text_width = right - left
    text_height = bottom - top

    # 이미지 생성 (여백 추가)
    padding = 20
    image_width = text_width + 2 * padding
    image_height = text_height + 2 * padding
    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)

    # 텍스트 그리기
    draw.text((padding, padding), text, font=font, fill='black')

    # 이미지 저장
    image.save(output_filename)