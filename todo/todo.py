"""
할 일 관리 앱 (todo.py)

함수 · 조건문 · 반복문 연습.

  터미널에서:  python todo.py
  웹에서:      index.html 이 이 파일을 그대로 불러와 브라우저 안에서 실행 (Pyodide)
"""

# 할 일 목록. 항목 하나는 {"title": "내용", "done": True/False} 딕셔너리
todos = []


# ---------------------------------------------------------------
# 함수 — 앱이 할 수 있는 일 하나하나를 이름 붙여 묶어 둔다
# ---------------------------------------------------------------

def add_todo(title):
    """할 일을 추가하고 결과 메시지를 돌려준다."""
    title = title.strip()              # 앞뒤 공백 제거
    if title == "":                    # 조건문: 빈 내용은 거부
        return "할 일 내용을 입력하세요."
    if len(title) > 40:
        return "할 일은 40자 이내로 적어 주세요."
    todos.append({"title": title, "done": False})
    return f"추가했습니다: {title}"


def complete_todo(number):
    """number번(1부터 시작) 할 일을 완료 처리한다."""
    if number < 1 or number > len(todos):      # 조건문: 번호 범위 검사
        return f"{number}번 할 일이 없습니다."
    item = todos[number - 1]
    if item["done"]:
        return f"이미 완료한 할 일입니다: {item['title']}"
    item["done"] = True
    return f"완료했습니다: {item['title']}"


def delete_todo(number):
    """number번 할 일을 삭제한다."""
    if number < 1 or number > len(todos):
        return f"{number}번 할 일이 없습니다."
    item = todos.pop(number - 1)       # 꺼내면서 목록에서 제거
    return f"삭제했습니다: {item['title']}"


def clear_done():
    """완료한 할 일을 모두 지우고, 지운 개수를 돌려준다."""
    remaining = []
    removed = 0
    for item in todos:                 # 반복문: 하나씩 살펴보며
        if item["done"]:               # 조건문: 완료면 세고
            removed += 1
        else:                          # 아니면 남긴다
            remaining.append(item)
    todos.clear()
    todos.extend(remaining)
    return removed


def count_done():
    """완료한 할 일 개수를 센다."""
    count = 0
    for item in todos:
        if item["done"]:
            count += 1
    return count


def format_list():
    """할 일 목록을 한 줄에 하나씩 정리한 문자열로 돌려준다."""
    if len(todos) == 0:
        return "할 일이 없습니다."
    lines = []
    for i, item in enumerate(todos, start=1):   # 반복문: 번호와 항목을 같이 꺼냄
        if item["done"]:
            mark = "[x]"
        else:
            mark = "[ ]"
        lines.append(f"{i}. {mark} {item['title']}")
    return "\n".join(lines)


def summary():
    """진행 상황을 한 줄로 요약한다."""
    total = len(todos)
    done = count_done()
    if total == 0:
        return "할 일을 추가해 보세요."
    percent = done * 100 // total
    if percent == 100:                 # 조건문: 진행률에 따라 다른 한마디
        comment = "모두 끝냈어요!"
    elif percent >= 50:
        comment = "절반 넘게 했어요."
    elif done == 0:
        comment = "아직 시작 전이에요."
    else:
        comment = "조금씩 해 봐요."
    return f"{done}/{total} 완료 ({percent}%) · {comment}"


# ---------------------------------------------------------------
# 터미널용 메뉴 — 웹에서는 index.html 이 이 역할을 대신한다
# ---------------------------------------------------------------

MENU = "[a] 추가  [d] 완료  [x] 삭제  [c] 완료 항목 정리  [q] 종료"


def ask_number(prompt):
    """번호를 입력받는다. 숫자가 아니면 0을 돌려준다."""
    text = input(prompt).strip()
    if text.isdigit():
        return int(text)
    return 0


def main():
    print("=== 할 일 관리 ===")
    while True:                                   # 반복문: 종료를 고를 때까지 계속
        print()
        print(format_list())
        print(summary())
        print(MENU)
        choice = input("> ").strip().lower()

        if choice == "a":                         # 조건문: 고른 메뉴에 따라 다른 함수 호출
            print(add_todo(input("할 일: ")))
        elif choice == "d":
            print(complete_todo(ask_number("완료할 번호: ")))
        elif choice == "x":
            print(delete_todo(ask_number("삭제할 번호: ")))
        elif choice == "c":
            print(f"완료한 할 일 {clear_done()}개를 정리했습니다.")
        elif choice == "q":
            print("안녕히 가세요.")
            break                                 # 반복문 빠져나가기 = 프로그램 종료
        else:
            print("a, d, x, c, q 중에서 골라 주세요.")


if __name__ == "__main__":
    main()
