

import streamlit as st

st.title("나의 첫 Streamlit 앱")

st.header("Streamlit에 오신 것을 환영합니다!")

st.write("이것은 간단한 텍스트입니다.")

st.success("성공적으로 앱이 실행되었습니다! 🎉")

💙 FITS 파일

1.  FITS 파일: 천문학에서 표준으로 사용되는 이미지 및 데이터 저장 형식

    🐰 header + binary data 영역으로 구성

    🐰 header 영역: 관측 시간, 망원경 정보, 필터, 노출 시간 등의 정보 기록 

    🐰 binary data 영역: 이미지 

2. FITS 파일을 열 때 사용되는 라이브러리: astropy 라이브러리

   : www.astropy.org/

    🐰 FITS 파일 읽기/쓰기/편집, 천체 좌표계 간 변환 (적경/적 위 ↔ 은하계 등), 천문학용 시간 변환 (UTC, TT, JD 등), 함수 모델링, 피팅 (예: 별 밝기 프로파일 등)

3. FITS 파일을 구할 수 있는 사이트

미국 내 지상망원경 관측자료 열람 사이트 

MAST 

SDSS 

           🐰관측 대상은 메시에 목록에서 정해봅시다.

           🐰나무위키: 메시에 목록 


web search 접속


대상 천체 입력, get coordinates 버튼 클릭


search 버튼 클릭


이미지 선택 후 다운로드(selected files 눌러 다운로드)


오른쪽 partial list of staged files에서

manifest as csv 버튼 눌러 다운
엑셀 열어서 다운로드 링크 복사
크롬창에 붙여넣기 하면 다운로드 진행됨

4. 천문 이미지 파일(FITS 파일) 저장 드라이브 


💚 FITS 파일 활용한 천문 이미지 처리 앱 제작해보기

1.  streamlit 앱에 FITS 파일을 업로드 하면 이미지를 분석해주는 앱 제작
    🐰프롬프트 예시: " 너는 파이썬과 Streamlit에 능숙한 전문가야.

나는 Streamlit으로 사용자가 FITS 파일을 업로드하면, 그 이미지를 시각화하고 기본적인 정보(예: 밝기, 이미지 크기, 노출시간)를 분석해주는 웹 앱을 만들고 싶어.


이 앱을 GitHub에 올릴 수 있도록 전체 Python 코드를 작성해줘."

2. 다음 코드를 github 'main.py'에 입력해보세요.

import streamlit as st

import numpy as np

from astropy.io import fits

from PIL import Image

from astropy.coordinates import SkyCoord, EarthLocation, AltAz

from astropy.time import Time

from datetime import datetime


# --- Streamlit 앱 페이지 설정 ---

st.set_page_config(page_title="천문 이미지 분석기", layout="wide")

st.title("🔭 천문 이미지 처리 앱")


# --- 파일 업로더 ---

uploaded_file = st.file_uploader(

    "분석할 FITS 파일을 선택하세요.",

    type=['fits', 'fit', 'fz']

)


# --- 서울 위치 설정 (고정값) ---

seoul_location = EarthLocation(lat=37.5665, lon=126.9780, height=50)  # 서울 위도/경도/고도


# --- 현재 시간 (UTC 기준) ---

now = datetime.utcnow()

now_astropy = Time(now)


# --- 파일이 업로드되면 실행될 로직 ---

if uploaded_file:

    try:

        with fits.open(uploaded_file) as hdul:

            image_hdu = None

            for hdu in hdul:

                if hdu.data is not None and hdu.is_image:

                    image_hdu = hdu

                    break


            if image_hdu is None:

                st.error("파일에서 유효한 이미지 데이터를 찾을 수 없습니다.")

            else:

                header = image_hdu.header

                data = image_hdu.data

                data = np.nan_to_num(data)


                st.success(f"**'{uploaded_file.name}'** 파일을 성공적으로 처리했습니다.")

                col1, col2 = st.columns(2)


                with col1:

                    st.header("이미지 정보")

                    st.text(f"크기: {data.shape[1]} x {data.shape[0]} 픽셀")

                    if 'OBJECT' in header:

                        st.text(f"관측 대상: {header['OBJECT']}")

                    if 'EXPTIME' in header:

                        st.text(f"노출 시간: {header['EXPTIME']} 초")


                    st.header("물리량")

                    mean_brightness = np.mean(data)

                    st.metric(label="이미지 전체 평균 밝기", value=f"{mean_brightness:.2f}")


                with col2:

                    st.header("이미지 미리보기")

                    if data.max() == data.min():

                        norm_data = np.zeros(data.shape, dtype=np.uint8)

                    else:

                        scale_min = np.percentile(data, 5)

                        scale_max = np.percentile(data, 99.5)

                        data_clipped = np.clip(data, scale_min, scale_max)

                        norm_data = (255 * (data_clipped - scale_min) / (scale_max - scale_min)).astype(np.uint8)


                    img = Image.fromarray(norm_data)

                    st.image(img, caption="업로드된 FITS 이미지", use_container_width=True)



                # --- 사이드바: 현재 천체 위치 계산 ---

                st.sidebar.header("🧭 현재 천체 위치 (서울 기준)")


                if 'RA' in header and 'DEC' in header:

                    try:

                        target_coord = SkyCoord(ra=header['RA'], dec=header['DEC'], unit=('hourangle', 'deg'))

                        altaz = target_coord.transform_to(AltAz(obstime=now_astropy, location=seoul_location))

                        altitude = altaz.alt.degree

                        azimuth = altaz.az.degree


                        st.sidebar.metric("고도 (°)", f"{altitude:.2f}")

                        st.sidebar.metric("방위각 (°)", f"{azimuth:.2f}")

                    except Exception as e:

                        st.sidebar.warning(f"천체 위치 계산 실패: {e}")

                else:

                    st.sidebar.info("FITS 헤더에 RA/DEC 정보가 없습니다.")


    except Exception as e:

        st.error(f"파일 처리 중 오류가 발생했습니다: {e}")

        st.warning("파일이 손상되었거나 유효한 FITS 형식이 아닐 수 있습니다.")

else:

    st.info("시작하려면 FITS 파일을 업로드해주세요.")


# --- 💬 댓글 기능 (세션 기반) ---

st.divider()

st.header("💬 의견 남기기")


if "comments" not in st.session_state:

    st.session_state.comments = []


with st.form(key="comment_form"):

    name = st.text_input("이름을 입력하세요", key="name_input")

    comment = st.text_area("댓글을 입력하세요", key="comment_input")

    submitted = st.form_submit_button("댓글 남기기")


    if submitted:

        if name.strip() and comment.strip():

            st.session_state.comments.append((name.strip(), comment.strip()))

            st.success("댓글이 저장되었습니다.")

        else:

            st.warning("이름과 댓글을 모두 입력해주세요.")


if st.session_state.comments:

    st.subheader("📋 전체 댓글")

    for i, (n, c) in enumerate(reversed(st.session_state.comments), 1):

        st.markdown(f"**{i}. {n}**: {c}")

else:

    st.info("아직 댓글이 없습니다. 첫 댓글을 남겨보세요!")
