from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import subprocess
from moviepy.editor import VideoFileClip

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'  # 업로드 폴더 설정
app.config['ALLOWED_EXTENSIONS'] = {'mp4'}  # 허용되는 파일 확장자 설정
app.config['RESULTS_FOLDER'] = 'results'  # 결과 폴더 설정

# 업로드 폴더가 존재하지 않으면 생성
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 결과 폴더가 존재하지 않으면 생성
if not os.path.exists(app.config['RESULTS_FOLDER']):
    os.makedirs(app.config['RESULTS_FOLDER'])

# 파일 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('base/index.html')  # 메인 페이지 렌더링

@app.route('/about')
def about():
    return render_template('base/about.html')  # about 페이지 렌더링

@app.route('/img_processing')
def img_processing():
    return render_template('base/img_processing.html')  # 이미지 처리 페이지 렌더링

@app.route('/img_choose')
def img_choose():
    return render_template('base/img_choose.html')  # 이미지 선택 페이지 렌더링

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)  # 파일이 없을 경우 리다이렉트
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)  # 파일명이 없을 경우 리다이렉트
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 추적 스크립트 실행
        reid_model_path = 'osnet_x0_25_msmt17.pt'  # reid 모델 불러오기
        project_path = app.config['RESULTS_FOLDER']  # 결과를 저장할 디렉토리 설정
        name = filename.rsplit('.', 1)[0]

        try:
            command = f'python tracking/track.py --source {file_path} --reid-model {reid_model_path} --save --project {project_path} --name {name} --save-id-crops --show-conf'
            subprocess.check_call(command, shell=True)

            # 출력 비디오를 moviepy를 사용하여 mp4 형식으로 변환
            input_video_path = os.path.join(project_path, name, f'{name}.avi')
            output_video_path = os.path.join(project_path, name, f'{name}.mp4')
            video_clip = VideoFileClip(input_video_path)
            video_clip.write_videofile(output_video_path, codec='libx264')
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}"

        return redirect(url_for('result', name=name))

@app.route('/result')
def result():
    name = request.args.get('name')
    video_path = f"{name}/{name}.mp4"
    return render_template('base/img_result.html', video_path=video_path)

@app.route('/results/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)  # 결과 파일 다운로드

if __name__ == "__main__":
    app.run(debug=True)
