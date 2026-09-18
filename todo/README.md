# 오늘의 할 일 (todo)

함수 · 조건문 · 반복문 연습용 할 일 관리 앱.

- `todo.py` — 앱 로직. 터미널에서 `python todo.py` 로 실행하면 메뉴가 뜹니다.
- `index.html` — 같은 `todo.py` 를 [Pyodide](https://pyodide.org)로 브라우저 안에서 실행하는 웹 UI.
  버튼을 누르면 어떤 Python 함수가 호출됐는지 아래 콘솔에 표시됩니다.

## 함수 구성

| 함수 | 하는 일 | 쓰인 문법 |
|---|---|---|
| `add_todo(title)` | 할 일 추가 (빈 내용·40자 초과 거부) | 조건문 |
| `complete_todo(number)` | n번 완료 처리 (범위·중복 검사) | 조건문 |
| `delete_todo(number)` | n번 삭제 | 조건문 |
| `clear_done()` | 완료한 항목 모두 제거, 개수 반환 | 반복문 + 조건문 |
| `count_done()` | 완료 개수 세기 | 반복문 + 조건문 |
| `format_list()` | 목록을 `1. [x] 내용` 형식 문자열로 | 반복문 + 조건문 |
| `summary()` | 진행률과 한마디 | 조건문 |
| `main()` | 터미널 메뉴 루프 | `while` + `if/elif` + `break` |

## 배포 (Cloudflare)

```
cd todo
npx wrangler deploy
```
