# 관악구 주택 유형별 소유권 이전 특성 분석 및 예측

팀 LauD(Laus + IPUD) · 박병주, 서정원, 이수경 — 팀 프로젝트 제안 페이지

- 발행: https://gwanak-property-forecast.tnrud3.workers.dev
- 코드: https://github.com/slee716-sk/assignment/tree/main/project-gwanak-forecast
- 원문: [노션 제안서](https://snu-laus.notion.site/42032921929280d5b047fc6239985230) (2026-11-22 수정본 기준)

## 담은 내용

노션 제안서의 1~7절을 빠짐없이 옮겼다.

1. 팀명 · 팀원 · 역할 분담
2. 프로젝트 유형과 목표 — 연구 질문 RQ1~3, 가설, 목표, 대상 및 선정 이유
3. 사용할 데이터와 출처, 공간 단위, 기간 — 데이터 6종 표, 분석·집계 단위, 관측·예측기간, 좌표계
4. 사용할 지표 — 소유권 이전율 식, 설명변수 표, 용도 혼합도(Normalized Shannon Entropy) 식, 정비구역 세 집단 분류 기준
5. 공간분석 기법 — 공간결합·버퍼·보행 네트워크·공간 자기상관·정비구역 이력 비교
6. 예측 대상(y)과 후보 모형 — 주택 유형별 Ridge / Random Forest, 학습·검증·시험 연도 구분, 평가 방법
7. 서비스 화면 스케치 — 스케치 그림, 사용자 조작 항목과 화면 구성

노션의 수식 그림 두 장은 HTML로 다시 조판했고, 화면 스케치는 용량을 줄여(WebP 100KB, JPG 대체본) 넣었다. 데이터 링크의 추적용 `utm_source` 매개변수는 뺐다.

## 파일 구성

| 경로 | 내용 |
|---|---|
| `public/index.html` | 제안 페이지 본문 |
| `public/style.css` | 과제3과 같은 색·서체 체계, 휴대폰에서는 표를 카드처럼 쌓아 보여줌 |
| `public/assets/service-sketch.*` | 서비스 화면 스케치 (노션 첨부 그림) |
| `wrangler.jsonc` | `public/`만 올리는 Cloudflare 설정 |

분석 데이터(소유자 자료 등)는 이 저장소에 넣지 않았다.

## 로컬 보기와 재발행

```powershell
python -m http.server 8765 --directory public
# 브라우저: http://127.0.0.1:8765
```

이 폴더에서 실행한다. 기존 계정으로 Wrangler 로그인이 되어 있어야 한다.

```powershell
npx wrangler@4.149.0 deploy
```

기존 과제와 같은 수동 발행 방식이다. GitHub push만으로 자동 배포되지는 않는다. Worker 이름은 `gwanak-property-forecast`이고 업로드 범위는 `public/`다.
