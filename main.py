
import json
import math
import re
import time
from pathlib import Path


# ==========================================
# Mini NPU Simulator
# 6단계: MAC 연산 성능 분석
# ==========================================

EPSILON = 1e-9
REPEAT = 10
SIZES = (3, 5, 13, 25)


# ------------------------------------------
# 1. MAC 연산 함수
# ------------------------------------------
def mac_operation(pattern, filter_data):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


# ------------------------------------------
# 2. 점수 비교 및 판정
# ------------------------------------------
def classify(score_a, score_b,
             label_a="A", label_b="B"):

    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b


# ------------------------------------------
# 3. 라벨 정규화
# ------------------------------------------
def normalize_label(label):
    if not isinstance(label, str):
        return None

    label = label.strip().lower()

    if label in ("+", "cross"):
        return "Cross"

    if label == "x":
        return "X"

    return None


# ------------------------------------------
# 4. 2차원 배열 검증
# ------------------------------------------
def validate_matrix(matrix, size):
    if not isinstance(matrix, list):
        raise ValueError("2차원 배열이 아닙니다.")

    if len(matrix) != size:
        raise ValueError(
            f"행 개수 불일치: {size}개 필요, "
            f"실제 {len(matrix)}개"
        )

    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(
                f"{i + 1}행이 리스트가 아닙니다."
            )

        if len(row) != size:
            raise ValueError(
                f"{i + 1}행 열 개수 불일치: "
                f"{size}개 필요, 실제 {len(row)}개"
            )

        for value in row:
            if type(value) not in (int, float):
                raise ValueError(
                    f"{i + 1}행에 숫자가 아닌 값이 있습니다."
                )

            if not math.isfinite(value):
                raise ValueError(
                    f"{i + 1}행에 유효하지 않은 숫자가 있습니다."
                )

    return True


# ------------------------------------------
# 5. 사용자 3x3 배열 입력
# ------------------------------------------
def input_matrix(name):
    matrix = []

    print(f"\n{name} (3줄 입력, 공백 구분)")
    print("취소하려면 q를 입력하세요.")

    for i in range(3):
        while True:
            line = input(f"{i + 1}행: ").strip()

            if line.lower() == "q":
                return None

            values = line.split()

            if len(values) != 3:
                print(
                    "입력 형식 오류: "
                    "각 줄에 3개의 숫자를 입력하세요."
                )
                continue

            try:
                row = [float(v) for v in values]

                if not all(math.isfinite(v) for v in row):
                    print("유한한 숫자만 입력하세요.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("입력 오류: 숫자만 입력하세요.")

    return matrix


# ------------------------------------------
# 6. 배열 출력
# ------------------------------------------
def print_matrix(name, matrix):
    print(f"\n{name}")

    for row in matrix:
        print(" ".join(f"{value:g}" for value in row))


# ------------------------------------------
# 7. 성능 측정 함수
# ------------------------------------------
def measure_mac(pattern, filter_data, repeat=REPEAT):
    total_time = 0.0

    for _ in range(repeat):
        start = time.perf_counter()

        mac_operation(pattern, filter_data)

        end = time.perf_counter()

        total_time += (end - start) * 1000

    return total_time / repeat


# ------------------------------------------
# 8. 크기별 십자가 패턴 생성
# ------------------------------------------
def generate_cross(size):
    matrix = []
    center = size // 2

    for i in range(size):
        row = []

        for j in range(size):
            if i == center or j == center:
                row.append(1.0)
            else:
                row.append(0.0)

        matrix.append(row)

    return matrix


# ------------------------------------------
# 9. 크기별 성능 분석
# ------------------------------------------
def performance_analysis():
    print("\n" + "=" * 48)
    print("[성능 분석] MAC 연산 평균 시간")
    print("=" * 48)

    print(f"측정 기준: 크기별 {REPEAT}회 반복")
    print("측정 대상: MAC 함수 1회 호출")
    print()

    print("-" * 48)
    print(
        f"{'크기':<10}"
        f"{'평균 시간(ms)':>18}"
        f"{'연산 횟수':>15}"
    )
    print("-" * 48)

    for size in SIZES:
        pattern = generate_cross(size)
        filter_data = generate_cross(size)

        average_time = measure_mac(
            pattern, filter_data, REPEAT
        )

        operations = size * size

        print(
            f"{size}x{size:<7}"
            f"{average_time:>18.6f}"
            f"{operations:>15}"
        )

    print("-" * 48)
    print("시간 복잡도: O(N^2)")
    print("※ 측정 시간은 실행 환경에 따라 달라집니다.")
    print()


# ------------------------------------------
# 10. 사용자 입력 모드
# ------------------------------------------
def user_input_mode():
    print("\n" + "=" * 40)
    print("[1] 필터 입력")
    print("=" * 40)

    filter_a = input_matrix("필터 A")

    if filter_a is None:
        print("입력을 취소하고 메뉴로 돌아갑니다.\n")
        return

    filter_b = input_matrix("필터 B")

    if filter_b is None:
        print("입력을 취소하고 메뉴로 돌아갑니다.\n")
        return

    print("\n[필터 저장 확인]")
    print_matrix("필터 A", filter_a)
    print_matrix("필터 B", filter_b)

    print("\n" + "=" * 40)
    print("[2] 패턴 입력")
    print("=" * 40)

    pattern = input_matrix("패턴")

    if pattern is None:
        print("입력을 취소하고 메뉴로 돌아갑니다.\n")
        return

    print_matrix("입력한 패턴", pattern)

    print("\n" + "=" * 40)
    print("[3] MAC 연산 결과")
    print("=" * 40)

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    result = classify(score_a, score_b)

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정 결과: {result}")

    print("\n" + "=" * 40)
    print("[4] 성능 분석 (3x3)")
    print("=" * 40)

    time_a = measure_mac(pattern, filter_a)
    time_b = measure_mac(pattern, filter_b)

    average = (time_a + time_b) / 2

    print(f"평균 MAC 시간: {average:.6f} ms")
    print("연산 횟수: 9 (필터 1개 기준)")

    print("\n사용자 입력 모드 완료!\n")


# ------------------------------------------
# 11. JSON 파일 불러오기
# ------------------------------------------
def load_json():
    file_path = Path(__file__).resolve().with_name(
        "data.json"
    )

    if not file_path.is_file():
        print("\n오류: data.json 파일이 없습니다.")
        return None

    try:
        with file_path.open(
            "r", encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        print(f"\nJSON 읽기 오류: {e}")
        return None

    if not isinstance(data, dict):
        print("JSON 오류: 최상위 데이터가 객체가 아닙니다.")
        return None

    if not isinstance(data.get("filters"), dict):
        print("JSON 오류: filters 객체가 없습니다.")
        return None

    if not isinstance(data.get("patterns"), dict):
        print("JSON 오류: patterns 객체가 없습니다.")
        return None

    return data


# ------------------------------------------
# 12. JSON 필터 가져오기
# ------------------------------------------
def get_filters(filters, size):
    size_key = f"size_{size}"

    if size_key not in filters:
        raise ValueError(
            f"{size_key} 필터가 없습니다."
        )

    filter_group = filters[size_key]

    if not isinstance(filter_group, dict):
        raise ValueError(
            f"{size_key} 필터 형식 오류"
        )

    normalized = {}

    for key, matrix in filter_group.items():
        label = normalize_label(key)

        if label is None:
            continue

        if label in normalized:
            raise ValueError(
                f"{size_key}의 {label} 필터 중복"
            )

        validate_matrix(matrix, size)
        normalized[label] = matrix

    if "Cross" not in normalized:
        raise ValueError("Cross 필터가 없습니다.")

    if "X" not in normalized:
        raise ValueError("X 필터가 없습니다.")

    return normalized["Cross"], normalized["X"]


# ------------------------------------------
# 13. JSON 케이스 분석
# ------------------------------------------
def analyze_case(case_id, case_data, filters):
    match = re.fullmatch(
        r"size_(\d+)_(\d+)", case_id
    )

    if match is None:
        raise ValueError(
            "패턴 키 오류: size_N_idx 형식 필요"
        )

    size = int(match.group(1))

    if size not in (5, 13, 25):
        raise ValueError(
            f"지원하지 않는 크기: {size}"
        )

    if not isinstance(case_data, dict):
        raise ValueError("패턴 데이터 형식 오류")

    if "input" not in case_data:
        raise ValueError("input 항목 없음")

    if "expected" not in case_data:
        raise ValueError("expected 항목 없음")

    expected = normalize_label(
        case_data["expected"]
    )

    if expected is None:
        raise ValueError(
            f"expected 라벨 오류: {case_data['expected']}"
        )

    pattern = case_data["input"]

    validate_matrix(pattern, size)

    cross_filter, x_filter = get_filters(
        filters, size
    )

    cross_score = mac_operation(
        pattern, cross_filter
    )

    x_score = mac_operation(
        pattern, x_filter
    )

    result = classify(
        cross_score, x_score, "Cross", "X"
    )

    print(f"Cross 점수: {cross_score}")
    print(f"X 점수: {x_score}")
    print(f"판정: {result}")
    print(f"expected: {expected}")

    if result == expected:
        print("결과: PASS")
        return True, ""

    if result == "UNDECIDED":
        reason = (
            "동점(UNDECIDED) 처리로 "
            "예상값과 불일치"
        )
    else:
        reason = (
            f"판정 불일치: "
            f"예상 {expected}, 실제 {result}"
        )

    print(f"결과: FAIL ({reason})")
    return False, reason


# ------------------------------------------
# 14. data.json 분석 모드
# ------------------------------------------
def json_analysis_mode():
    print("\n" + "=" * 40)
    print("[1] JSON 데이터 로드")
    print("=" * 40)

    data = load_json()

    if data is None:
        print("메인 메뉴로 돌아갑니다.\n")
        return

    filters = data["filters"]
    patterns = data["patterns"]

    print("data.json 로드 완료!")

    for size in (5, 13, 25):
        try:
            get_filters(filters, size)
            print(
                f"size_{size} 필터 확인 완료 "
                "(Cross, X)"
            )

        except ValueError as e:
            print(f"size_{size} 필터 오류: {e}")

    print("\n" + "=" * 40)
    print("[2] 패턴 자동 분석")
    print("=" * 40)

    total = 0
    passed = 0
    failed = 0
    failure_list = []

    for case_id, case_data in patterns.items():
        total += 1
        print(f"\n--- {case_id} ---")

        try:
            success, reason = analyze_case(
                case_id, case_data, filters
            )

            if success:
                passed += 1

            else:
                failed += 1
                failure_list.append(
                    (case_id, reason)
                )

        except (ValueError, TypeError, OverflowError) as e:
            failed += 1
            reason = str(e)

            print(f"결과: FAIL ({reason})")
            failure_list.append(
                (case_id, reason)
            )

    # JSON 분석 후 성능 측정
    performance_analysis()

    print("\n" + "=" * 40)
    print("[4] 결과 요약")
    print("=" * 40)

    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")

    if failure_list:
        print("\n[실패 케이스 목록]")

        for case_id, reason in failure_list:
            print(f"- {case_id}: {reason}")
    else:
        print("\n모든 테스트 통과!")

    print("\nJSON 분석 모드 완료!\n")


# ------------------------------------------
# 15. 기본 메뉴
# ------------------------------------------
def show_menu():
    print("=" * 40)
    print("       Mini NPU Simulator")
    print("=" * 40)

    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("0. 프로그램 종료")
    print()


# ------------------------------------------
# 16. 메인 함수
# ------------------------------------------
def main():
    while True:
        show_menu()

        choice = input("선택: ").strip()

        if choice == "1":
            user_input_mode()

        elif choice == "2":
            json_analysis_mode()

        elif choice == "0":
            print("\n프로그램을 종료합니다.")
            break

        else:
            print("\n잘못된 입력입니다.")
            print("0, 1, 2 중 하나를 입력하세요.\n")


# ------------------------------------------
# 17. 프로그램 시작
# ------------------------------------------
if __name__ == "__main__":
    try:
        main()

    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")
