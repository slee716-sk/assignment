# 과제3 · 서울 빈집의 접도 조건과 해소신호

서울 자치구별 빈집의 접도 제약은 어떻게 다르며, 해소신호 발생률과 어떤 관계가 있는가?

- 발행: https://seoul-vacancy-study.tnrud3.workers.dev
- 코드: https://github.com/slee716-sk/assignment/tree/main/assignment3-vacancy
- 분석 범위: 서울 25개 자치구, 연구의 비집합 빈집 고정 표본 2,825채.
- 원자료 추출: 2026-10-30. 관측 종료: 2026-04-30. 접도 지표 보강: 2026-11-01.

## 지표와 결과

1. **해소신호 발생률** = 첫 해소신호 주택 수 / 관찰 호·년 합 × 100. 한 집의 판정일부터 첫 신호 또는 종료일까지 관찰하며, 한 집은 첫 신호 한 번만 센다. 높을수록 관찰시간당 신호가 빈번하다. 실제 활용 완료율이나 연간 해소확률이 아니다.
2. **접도 제약 빈집 비율** = 맹지·차량통행 불가 범주 주택 수 / 도로접면이 확인되는 표본 수 × 100. 높을수록 표본에서 접도 제약 비중이 높다. 도로 정보가 없는 집은 분모에서 제외한다.

서울 전체 발생률은 618 / 7,448.695414 × 100 = **8.30건/100호·년**이다. 접도는 유효 2,821채 중 1,574채, **55.8%**이며 4채는 미확인이다. 표본과 접도 유효 표본이 각각 30채 이상인 20개 구의 순위상관은 전체기간 **-0.46**, 첫 18개월 **-0.22**다. 접도 조건만으로 해소신호의 지역 차이를 설명할 수 없으며, 구 단위 연관을 개별 주택의 인과관계로 옮기지 않는다.

공개 페이지에는 두 주제도, 발생률·신뢰구간 그래프, 접도 비율과 발생률 산점도, 기간·소표본 전환, 구 선택 연동, 계산식·전처리·한계, 결과표 및 CSV/PNG 다운로드를 담았다.

## 파일 구성

| 경로 | 내용 |
|---|---|
| `public/` | Cloudflare에 배포하는 정적 보고서·구별 집계·그림만 포함 |
| `analysis.py` | 고정된 비공개 입력에서 집별 관찰시간, 두 지표, 상관, 지도·그림을 산출하는 Python 코드 |
| `tests.py` | 사건일·관찰기간, 접도 분류, 결측 분모, 자료 없음과 0건 구분 테스트 |
| `verify_aggregates.py` | 공개 CSV/JSON의 식·구별 합계·순위상관을 표준 라이브러리로 검산 |
| `input_manifest.json` | 발행 당시 입력의 열 목록·행 수·SHA-256. 개별 기록은 없음 |
| `data/seoul_boundary_2015.geojson` | 공개 서울 자치구 경계. 출처·라이선스는 아래 참고 |
| `wrangler.jsonc` | `public/`만 업로드하는 Cloudflare 설정 |

## 공개 자료로 검산하기

Python 3.12 이상에서 추가 패키지 설치 없이 실행한다.

```powershell
python verify_aggregates.py
```

이 명령은 공개된 25개 구 집계표에서 두 지표의 계산식, 구별 합계, 전체/18개월 및 20/25개 구의 스피어만 상관을 다시 계산한다. 집별 날짜와 원자료의 정확성까지 검증하는 명령은 아니다.

## 분석 코드와 테스트 실행

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest tests -v
```

분석 당시 Python 3.12를 사용했다. 그림에는 Windows의 Malgun Gothic 글꼴을 사용하며 다른 운영체제에서는 사용 가능한 한글 글꼴로 바꿔야 한다.

전체 분석의 재실행에는 권한 있는 사용자가 보유한 **발행 당시 고정 추출본** `seoul_minimal.csv`, `seoul_land.csv`가 필요하다. 이를 로컬 `private/`에 두고 실행한다. 이 폴더는 Git에서 제외된다.

```powershell
.\.venv\Scripts\python analysis.py
```

고정 추출본 대신 동일 시점의 연구 원자료에서 추출하려면 `VACANCY_RESEARCH_ROOT`를 연구 폴더로 지정할 수 있다. 이 경우 해당 폴더 아래 `work/national/전국빈집_집별_v2.csv`와 `공개자료/08_토지특성/서울_토지특성_api.csv`를 읽는다. 입력 해시가 `input_manifest.json`과 다르면 중단하여 다른 시점의 자료로 발행 표본이 조용히 바뀌지 않도록 했다.

개별 주소·필지·소유자 자료와 인증키는 저장소에 포함하지 않았다. 따라서 원자료가 없는 독자는 공개 집계의 검산까지 실행할 수 있으며, 집별 원자료 단계의 전체 재현에는 별도 자료 권한이 필요하다.

## 로컬 보기와 Cloudflare 재발행

```powershell
python -m http.server 8765 --directory public
# 브라우저: http://127.0.0.1:8765
```

이 폴더에서 다음 명령을 실행한다. 기존 계정으로 Wrangler 로그인이 되어 있어야 한다.

```powershell
npx wrangler@4.149.0 deploy
```

기존 과제와 같은 수동 발행 방식이다. GitHub push만으로 자동 배포되도록 연결한 설정은 아니다. Worker 이름은 `seoul-vacancy-study`이고 업로드 범위는 `public/`다. 분석 코드·README·설정·비공개 입력 폴더는 웹 자산으로 올리지 않는다.

## 자료와 해석 범위

- 연구용 통합 빈집 명부와 집별 v2 해소신호 자료: 2026-10-30 고정 추출. 서울 비집합 분석대상 표본과 기존 제외·보류 기준을 유지했다.
- 건축물대장 말소·변동 및 건축인허가: 첫 행정신호 정의에 사용. 허가는 실제 재사용 완료와 구분한다.
- [V-World](https://www.vworld.kr/) 토지특성 보관본: 판정 연도와 가장 가까운 기록을 선택하고 같은 거리이면 이전 연도를 우선했다. 도로접면의 맹지·세로(불) 동의어를 통합했다.
- [southkorea/seoul-maps · JUSO 2015](https://github.com/southkorea/seoul-maps/tree/master/juso/2015): 자치구 위치 표현용 경계, Apache 2.0. `public/NOTICE.txt` 및 `public/APACHE-2.0.txt` 참고. 2026년 세부 경계의 측량 자료가 아니다.
- [CDC incidence rate 계산 원리](https://archive.cdc.gov/www_cdc_gov/csels/dsepd/ss1978/lesson3/section2.html)를 주택·행정신호에 적용했다.

표본은 서울 전체 빈집의 대표표본이 아니다. 접도 비율은 법적 접도 요건이나 실제 차량 진입을 판정하지 않는다. 신뢰구간은 표본 선택·기록 누락·공간 군집을 모두 반영하지 않으며, 관찰기간을 반영해도 판정 연도와 표본 구성 차이가 남는다.
