import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                         QLabel, QLineEdit, QPushButton, QMessageBox, QFrame,
                         QFileDialog, QDialog, QComboBox, QScrollArea)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import yt_dlp
import urllib.request

class YouTubeThumbnailDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Thumbnail Downloader')
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QPushButton {
                padding: 5px 15px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #dcdcdc;
                border-radius: 3px;
            }
        """)

        main_layout = QVBoxLayout()

        # URL 입력 부분
        self.label = QLabel('Enter YouTube URL:')
        main_layout.addWidget(self.label)

        self.url_input = QLineEdit(self)
        main_layout.addWidget(self.url_input)

        self.download_button = QPushButton('Download Thumbnail', self)
        self.download_button.clicked.connect(self.download_thumbnail)
        main_layout.addWidget(self.download_button)

        # 썸네일과 정보를 담을 수평 레이아웃
        content_layout = QHBoxLayout()

        # 왼쪽 썸네일 부분
        self.thumbnail_label = QLabel(self)
        self.thumbnail_label.setFixedSize(320, 180)  # 16:9 비율로 고정
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFrameStyle(QFrame.Box)
        content_layout.addWidget(self.thumbnail_label)

        # 오른쪽 정보 부분
        info_layout = QVBoxLayout()
        
        self.likes_label = QLabel('Likes: -')
        self.likes_label.setStyleSheet('font-size: 14px; margin: 5px;')
        info_layout.addWidget(self.likes_label)

        self.comments_label = QLabel('Comments: -')
        self.comments_label.setStyleSheet('font-size: 14px; margin: 5px;')
        info_layout.addWidget(self.comments_label)

        self.views_label = QLabel('Views: -')
        self.views_label.setStyleSheet('font-size: 14px; margin: 5px;')
        info_layout.addWidget(self.views_label)

        # 다운로드 버튼 추가
        self.video_download_button = QPushButton('Download Video', self)
        self.video_download_button.clicked.connect(self.download_video)
        self.video_download_button.setStyleSheet('font-size: 14px; padding: 5px; margin: 5px;')
        info_layout.addWidget(self.video_download_button)

        info_layout.addStretch()
        content_layout.addLayout(info_layout)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def download_thumbnail(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Error', 'Please enter a YouTube URL.')
            return

        try:
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'force_generic_extractor': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
                
                # 좋아요 수, 댓글 수, 조회수 가져오기
                like_count = info.get('like_count', 0)
                comment_count = info.get('comment_count', 0)
                view_count = info.get('view_count', 0)
                
                # 레이블 업데이트
                self.likes_label.setText(f'Likes: {like_count:,}')
                self.comments_label.setText(f'Comments: {comment_count:,}')
                self.views_label.setText(f'Views: {view_count:,}')

                if thumbnail_url:
                    response = urllib.request.urlopen(thumbnail_url)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.read())
                    scaled_pixmap = pixmap.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    QMessageBox.information(self, 'Success', 'Data retrieved successfully!')
                else:
                    QMessageBox.warning(self, 'Error', 'Thumbnail not found.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Error', 'Please enter a YouTube URL.')
            return

        try:
            # FFmpeg 경로 설정
            ffmpeg_path = r"C:\Users\msi\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

            # 저장 경로 선택
            save_path = QFileDialog.getSaveFileName(
                self,
                'Save Video',
                '',
                'MP4 Files (*.mp4);;All Files (*.*)'
            )[0]

            if not save_path:  # 사용자가 취소를 누른 경우
                return

            # 포맷 정보 가져오기
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info['formats']
                  # 포맷 선택 다이얼로그 표시
                format_selector = FormatSelector(formats, self)
                format_selector.setWindowModality(Qt.ApplicationModal)
                if format_selector.exec_() == QDialog.Accepted:
                    selected_format = format_selector.get_selected_format()
                    if not selected_format:
                        QMessageBox.warning(self, '알림', '포맷을 선택하지 않았습니다.')
                        return
                else:
                    return

            # 다운로드 옵션 설정
            ydl_opts = {
                'format': selected_format,
                'outtmpl': save_path,
                'quiet': True,
                'ffmpeg_location': ffmpeg_path,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                QMessageBox.information(self, 'Download Started', 'Video download has started. Please wait...')
                ydl.download([url])
                QMessageBox.information(self, 'Success', 'Video downloaded successfully!')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while downloading: {str(e)}')

class FormatSelector(QDialog):
    def __init__(self, formats, parent=None):
        super().__init__(parent)
        self.setWindowTitle('비디오 포맷 선택')
        self.setMinimumWidth(600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.formats = formats
        self.selected_format = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 설명 레이블
        description = QLabel('다운로드할 비디오 포맷을 선택하세요:')
        description.setStyleSheet('font-size: 12pt; margin: 10px;')
        layout.addWidget(description)

        # 포맷 목록을 담을 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # 포맷별 버튼 생성
        for fmt in self.formats:
            format_widget = self.create_format_widget(fmt)
            scroll_layout.addWidget(format_widget)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # 닫기 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton('취소')
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #dcdcdc;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_format_widget(self, fmt):
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin: 2px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #f0f8ff;
                border: 1px solid #1e90ff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 포맷 정보
        info_layout = QVBoxLayout()
        
        # 해상도와 확장자
        resolution = fmt.get('resolution', 'N/A')
        if resolution == 'N/A' and 'width' in fmt and 'height' in fmt:
            resolution = f"{fmt['width']}x{fmt['height']}"
        
        format_label = QLabel()
        format_label.setStyleSheet('font-weight: bold; font-size: 11pt;')
        
        # 포맷 정보 구성
        format_info = []
        if resolution != 'N/A':
            format_info.append(f"해상도: {resolution}")
        if 'ext' in fmt:
            format_info.append(f"포맷: {fmt['ext']}")
        if 'filesize' in fmt:
            size_mb = fmt['filesize'] / (1024 * 1024)
            format_info.append(f"크기: {size_mb:.1f}MB")
        if 'vcodec' in fmt and fmt['vcodec'] != 'none':
            format_info.append(f"비디오 코덱: {fmt['vcodec']}")
        if 'acodec' in fmt and fmt['acodec'] != 'none':
            format_info.append(f"오디오 코덱: {fmt['acodec']}")
            
        format_label.setText(' | '.join(format_info))
        info_layout.addWidget(format_label)
        
        # fps 정보가 있다면 표시
        if 'fps' in fmt:
            fps_label = QLabel(f"FPS: {fmt['fps']}")
            fps_label.setStyleSheet('color: #666;')
            info_layout.addWidget(fps_label)
            
        layout.addLayout(info_layout)
        
        # 선택 버튼
        select_button = QPushButton('이 포맷 선택')
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        select_button.clicked.connect(lambda: self.select_format(fmt['format_id']))
        layout.addWidget(select_button)
        
        widget.setLayout(layout)
        return widget

    def select_format(self, format_id):
        self.selected_format = format_id
        self.accept()

    def get_selected_format(self):
        return self.selected_format

if __name__ == '__main__':
    print("Starting YouTube Thumbnail Downloader...")
    app = QApplication(sys.argv)
    downloader = YouTubeThumbnailDownloader()
    downloader.show()
    print("Application is running.")
    sys.exit(app.exec_())