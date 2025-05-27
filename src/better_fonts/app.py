from renderer import create_text_image
import os

from PIL import Image, ImageDraw, ImageFont
import os

def wrap_text(text, font, max_width):
    """
    텍스트를 주어진 최대 너비에 맞춰 여러 줄로 나눕니다.
    단어 단위로 줄바꿈을 시도합니다.
    """
    lines = []
    if not text:
        return lines

    words = text.split(' ') # 공백을 기준으로 단어 분리
    current_line = []
    current_line_width = 0
    space_width = font.getlength(' ') # 공백의 너비

    for word in words:
        # 단어의 너비 계산
        word_width = font.getlength(word)

        # 현재 줄에 단어를 추가했을 때 최대 너비를 초과하는지 확인
        if current_line_width + (space_width if current_line else 0) + word_width <= max_width:
            # 현재 줄에 단어 추가
            if current_line:
                current_line_width += space_width
            current_line.append(word)
            current_line_width += word_width
        else:
            # 최대 너비를 초과하면 새 줄 시작
            if current_line: # 현재 줄에 내용이 있다면 먼저 추가
                lines.append(" ".join(current_line))
            current_line = [word] # 새 줄에 현재 단어 추가
            current_line_width = word_width

            # 만약 단어 자체가 max_width를 초과하는 경우 (매우 긴 단어, URL 등)
            # 이 부분은 현재 단순하게 처리하며, 필요 시 글자 단위로 분할하는 로직 추가 가능
            while current_line_width > max_width:
                if len(current_line[0]) == 1: # 한 글자 단어가 max_width를 초과하는 경우는 거의 없음
                    break
                # 단어 자체가 너무 길어서 한 줄에 들어가지 않을 경우,
                # 여기서는 간단히 다음 줄로 넘기거나, 더 복잡한 로직으로 글자 단위 분할 가능
                lines.append(" ".join(current_line))
                current_line = []
                current_line_width = 0
                break # 이 단어는 이미 처리되었으므로 다음 단어로 넘어감

    if current_line: # 마지막 줄 처리
        lines.append(" ".join(current_line))

    return lines


def create_multiline_text_image(text_lines, font_path, font_size, output_filename, line_spacing=10):
    """
    여러 줄의 텍스트를 이미지로 생성합니다.

    Args:
        text_lines (list): 이미지로 변환할 텍스트 줄들의 리스트.
        font_path (str): 사용할 .ttf 폰트 파일의 경로.
        font_size (int): 폰트 크기.
        output_filename (str): 생성될 이미지 파일의 이름.
        line_spacing (int): 줄 간 간격 (픽셀).
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error: Font file not found or could not be opened at {font_path}")
        return

    # 각 줄의 크기를 미리 계산하여 전체 이미지 크기 결정
    max_line_width = 0
    total_text_height = 0
    line_heights = []

    for line in text_lines:
        # textbbox는 (left, top, right, bottom) 튜플을 반환
        bbox = ImageDraw.Draw(Image.new('RGB', (1,1))).textbbox((0,0), line, font=font)
        line_width = bbox[2] - bbox[0] # right - left
        line_height = bbox[3] - bbox[1] # bottom - top

        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)
        total_text_height += line_height

    # 이미지 생성 (여백 및 줄 간 간격 추가)
    padding = 30
    image_width = max_line_width + 2 * padding
    # 총 텍스트 높이 + (줄 수 - 1) * 줄 간 간격 + 상하 여백
    image_height = total_text_height + (len(text_lines) - 1) * line_spacing + 2 * padding
    
    # 최소 이미지 크기 보장 (텍스트가 없거나 매우 짧을 때)
    if image_width < 100: image_width = 100
    if image_height < 100: image_height = 100


    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)

    # 각 줄 그리기
    current_y = padding
    for i, line in enumerate(text_lines):
        draw.text((padding, current_y), line, font=font, fill='black')
        current_y += line_heights[i] + line_spacing

    # 이미지 저장
    image.save(output_filename)
    print(f"'{output_filename}' 이미지가 성공적으로 생성되었습니다.")


if __name__ == "__main__":
    example_text = """
    ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz
    0123456789 `~!@#$%^&*()-=_+\|<>,.;:/?"'[{]}
    별 헤는 밤, 낡은 짚차를 타고 숲 속으로, 퀘퀘한 향내를 맡으니 즈믄 강은 흐르고 저편에는 붉은 탑이 솟아있네.
    """
    font_size = 30
    output_base_name = "image" # 이미지 파일명 베이스

    # 생성된 이미지를 저장할 출력 폴더 지정
    output_folder = "output"
    # Docker 컨테이너 내부에서의 출력 폴더 경로
    docker_output_dir = os.path.join("/app", output_folder)

    # 출력 폴더가 없으면 생성
    os.makedirs(docker_output_dir, exist_ok=True) # exist_ok=True는 폴더가 이미 있어도 에러를 발생시키지 않음

    # Docker 컨테이너 내부의 폰트 디렉토리 경로
    docker_fonts_dir = os.path.join("/app", "fonts")

    # 폰트 디렉토리 내의 모든 .ttf 파일 찾기
    font_files = [f for f in os.listdir(docker_fonts_dir) if f.endswith('.ttf')]

    if not font_files:
        print(f"Error: No .ttf files found in {docker_fonts_dir}")
    else:
        # 최대 이미지 너비를 대략적으로 설정 (픽셀 단위)
        # 이 값은 폰트 크기와 텍스트 내용에 따라 조절해야 합니다.
        max_image_width = 800

        for font_file_name in font_files:
            # 각 폰트 파일의 전체 경로
            full_font_path = os.path.join(docker_fonts_dir, font_file_name)

            # 폰트 로드 (텍스트 줄바꿈을 위해 미리 로드)
            try:
                current_font = ImageFont.truetype(full_font_path, font_size)
            except IOError:
                print(f"Skipping {font_file_name}: Font file not found or could not be opened.")
                continue

            # 텍스트를 여러 줄로 나누기
            wrapped_lines = wrap_text(example_text.strip(), current_font, max_image_width - 2 * 20) # max_width에서 양쪽 padding 제외

            # 출력 이미지 파일명 (폰트 이름 포함)
            image_filename = f"{output_base_name}_{os.path.splitext(font_file_name)[0]}.png"
            # 최종 이미지 저장 경로: output 폴더 안에 파일명
            output_image_path = os.path.join(docker_output_dir, image_filename)

            print(f"Rendering text with {font_file_name} to {output_image_path}...")
            create_multiline_text_image(wrapped_lines, full_font_path, font_size, output_image_path)

    print("All font renderings completed.")