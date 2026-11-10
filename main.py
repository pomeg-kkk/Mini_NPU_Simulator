
import json
import math
import re
import time
from pathlib import Path


# ==========================================
# Mini NPU Simulator
# 필수 과제 + 보너스 1 + 보너스 2
# 평가 피드백 #2 보완 버전
# ==========================================

EPSILON = 1e-9
REPEAT = 10
BONUS_REPEAT = 1000
SIZES = (3, 5, 13, 25)


# ------------------------------------------
# 1. 기본 MAC 연산 (2차원)
# ------------------------------------------
def mac_operation(pattern, filter_data):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


# ------------------------------------------
# 2. 2차원 배열을 1차원으로 변환
# ------------------------------------------
def flatten_matrix(matrix):
    return [
        value
        for row in matrix
        for value in row
    ]


# ------------------------------------------
# 3. 1차원 MAC 연산 (보너스 1)
# ------------------------------------------
def mac_operation_flat(pattern, filter_data):
    if len(pattern) != len(filter_data):
        raise ValueError(
            "1차원 배열 길이가 일치하지 않습니다."
        )

    score = 0.0

    for i in range(len(pattern)):
        score += pattern[i] * filter_data[i]

    return score


# ------------------------------------------
# 4. MAC 점수 비교
# ------------------------------------------
def classify(
    score_a,
    score_b,
    label_a="A",
    label_b="B"
):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    return label_a if score_a > score_b else label_b


# ------------------------------------------
# 5. 평가 피드백 #2 보완
# 내부 판정값과 사용자 출력 문구 분리
# ------------------------------------------
def format_decision(result):
    if result == "UNDECIDED":
        return "판정 불가"

    return result


# ------------------------------------------
# 6. 라벨 정규화
# ------------------------------------------
def normalize_label(label):
    if not isinstance(label, str):
        return None

    text = label.strip().lower()

    if text in ("+", "cross"):
        return "Cross"

    if text == "x":
        return "X"

    return None


# ------------------------------------------
# 7. 행렬 검증
# ------------------------------------------
def validate_matrix(matrix, size):
    if not isinstance(matrix, list):
        raise ValueError(
            "2차원 리스트가 아닙니다."
        )

    if len(matrix) != size:
        raise ValueError(
            f"행 개수가 {size}개여야 합니다."
        )

    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(
                f"{i + 1}행이 리스트가 아닙니다."
            )

        if len(row) != size:
            raise ValueError(
                f"{i + 1}행의 열 개수가 "
                f"{size}개여야 합니다."
            )

        for value in row:
            if type(value) not in (int, float):
                raise ValueError(
                    "숫자만 허용합니다."
                )

            if not math.isfinite(value):
                raise ValueError(
                    "유한한 숫자만 허용합니다."
                )


# ------------------------------------------
# 8. 사용자 3x3 행렬 입력
# ------------------------------------------
def input_matrix(name):
    matrix = []

    print(f"\n{name}: 한 줄에 숫자 3개 입력")
    print("q를 입력하면 취소합니다.")

    for i in range(3):
        while True:
            line = input(
                f"{i + 1}행: "
            ).strip()

            if line.lower() == "q":
                return None

            values = line.split()

            if len(values) != 3:
                print(
                    "오류: 숫자를 정확히 "
                    "3개 입력하세요."
                )
                continue

            try:
                row = [
                    float(value)
                    for value in values
                ]

                if not all(
                    math.isfinite(value)
                    for value in row
                ):
                    print(
                        "오류: 유한한 숫자만 "
                        "입력하세요."
                    )
                    continue

                matrix.append(row)
                break

            except ValueError:
                print(
                    "오류: 숫자만 입력하세요."
                )

    return matrix


# ------------------------------------------
# 9. 행렬 출력
# ------------------------------------------
def print_matrix(title, matrix):
    print(f"\n[{title}]")

    for row in matrix:
        print(
            " ".join(
                f"{value:g}"
                for value in row
            )
        )


# ------------------------------------------
# 10. MAC 실행 시간 측정
# ------------------------------------------
def measure_mac(
    func,
    pattern,
    filter_data,
    repeat=REPEAT
):
    if repeat <= 0:
        raise ValueError(
            "반복 횟수는 1 이상이어야 합니다."
        )

    start = time.perf_counter()

    for _ in range(repeat):
        func(pattern, filter_data)

    end = time.perf_counter()

    return (end - start) * 1000 / repeat


# ------------------------------------------
# 11. Cross 패턴 생성
# ------------------------------------------
def generate_cross(size):
    center = size // 2

    return [
        [
            1.0
            if i == center or j == center
            else 0.0
            for j in range(size)
        ]
        for i in range(size)
    ]


# ------------------------------------------
# 12. X 패턴 생성
# ------------------------------------------
def generate_x(size):
    return [
        [
            1.0
            if i == j or i + j == size - 1
            else 0.0
            for j in range(size)
        ]
        for i in range(size)
    ]


# ------------------------------------------
# 13. 패턴 크기 입력
# ------------------------------------------
def input_pattern_size():
    while True:
        value = input(
            "패턴 크기 N "
            "(3~25 홀수, q=취소): "
        ).strip()

        if value.lower() == "q":
            return None

        try:
            size = int(value)

        except ValueError:
            print(
                "오류: 정수를 입력하세요."
            )
            continue

        if not (3 <= size <= 25):
            print(
                "오류: 3~25 사이의 "
                "숫자를 입력하세요."
            )
            continue

        if size % 2 == 0:
            print(
                "오류: 홀수를 입력하세요."
            )
            continue

        return size


# ------------------------------------------
# 14. 생성된 패턴 저장
# ------------------------------------------
def save_generated_patterns(storage):
    size = input_pattern_size()

    if size is None:
        return False

    cross_pattern = generate_cross(size)
    x_pattern = generate_x(size)

    storage.clear()

    storage.update({
        "size": size,
        "Cross": cross_pattern,
        "X": x_pattern
    })

    print(
        f"\n{size}x{size} Cross/X "
        "패턴 저장 완료!"
    )

    print(
        "모드 1과 성능 분석에서 "
        "재사용할 수 있습니다."
    )

    return True


# ------------------------------------------
# 15. 저장된 패턴 선택
# ------------------------------------------
def choose_generated_pattern(storage):
    if not storage:
        print("\n저장된 패턴이 없습니다.")
        print(
            "먼저 4번 메뉴에서 "
            "패턴을 생성하세요."
        )
        return None

    while True:
        size = storage["size"]

        print(
            f"\n[저장된 패턴: "
            f"{size}x{size}]"
        )

        print("1. Cross")
        print("2. X")
        print("q. 취소")

        choice = input(
            "선택: "
        ).strip().lower()

        if choice == "1":
            return "Cross"

        if choice == "2":
            return "X"

        if choice == "q":
            return None

        print(
            "1, 2 또는 q를 입력하세요."
        )


# ------------------------------------------
# 16. 저장 패턴 MAC 분석
# 평가 피드백 #2 반영
# ------------------------------------------
def analyze_generated_pattern(storage, label):
    pattern = storage[label]

    cross_filter = storage["Cross"]
    x_filter = storage["X"]

    print_matrix(
        f"재사용 패턴: {label}",
        pattern
    )

    cross_score = mac_operation(
        pattern,
        cross_filter
    )

    x_score = mac_operation(
        pattern,
        x_filter
    )

    result = classify(
        cross_score,
        x_score,
        "Cross",
        "X"
    )

    # 사용자에게 표시할 값만 변환
    display_result = format_decision(result)

    print("\n[MAC 분석 결과]")
    print(
        f"Cross 점수: {cross_score:g}"
    )
    print(
        f"X 점수: {x_score:g}"
    )
    print(f"판정: {display_result}")
    print(f"예상 정답: {label}")

    if result == label:
        print("테스트 결과: PASS")
    else:
        print("테스트 결과: FAIL")

    t_cross = measure_mac(
        mac_operation,
        pattern,
        cross_filter,
        REPEAT
    )

    t_x = measure_mac(
        mac_operation,
        pattern,
        x_filter,
        REPEAT
    )

    average = (t_cross + t_x) / 2

    print("\n[성능 측정]")
    print(
        f"평균 MAC 시간: "
        f"{average:.6f} ms"
    )
    print(
        f"반복 횟수: 필터별 {REPEAT}회"
    )
    print(
        f"원소 개수: "
        f"{storage['size'] ** 2}"
    )


# ------------------------------------------
# 17. 패턴 생성기 (보너스 2)
# ------------------------------------------
def pattern_generator_mode(storage):
    print("\n" + "=" * 48)
    print(
        "[보너스 2] "
        "Cross / X 패턴 자동 생성"
    )
    print("=" * 48)

    if not save_generated_patterns(storage):
        print(
            "패턴 생성을 취소했습니다."
        )
        return

    print_matrix(
        "Cross 패턴",
        storage["Cross"]
    )

    print_matrix(
        "X 패턴",
        storage["X"]
    )

    label = choose_generated_pattern(storage)

    if label is not None:
        analyze_generated_pattern(
            storage,
            label
        )


# ------------------------------------------
# 18. 직접 입력 모드 (3x3)
# 평가 피드백 #2 반영
# ------------------------------------------
def manual_input_mode():
    print("\n[3x3 직접 입력]")

    filter_a = input_matrix("필터 A")

    if filter_a is None:
        print("입력을 취소했습니다.")
        return

    filter_b = input_matrix("필터 B")

    if filter_b is None:
        print("입력을 취소했습니다.")
        return

    print_matrix("필터 A", filter_a)
    print_matrix("필터 B", filter_b)

    pattern = input_matrix("패턴")

    if pattern is None:
        print("입력을 취소했습니다.")
        return

    print_matrix("입력 패턴", pattern)

    score_a = mac_operation(
        pattern,
        filter_a
    )

    score_b = mac_operation(
        pattern,
        filter_b
    )

    result = classify(
        score_a,
        score_b
    )

    # 모드 1에서만 한국어 표시
    display_result = format_decision(result)

    print("\n[MAC 연산 결과]")
    print(f"A 점수: {score_a:g}")
    print(f"B 점수: {score_b:g}")
    print(
        f"판정 결과: {display_result}"
    )

    t_a = measure_mac(
        mac_operation,
        pattern,
        filter_a,
        REPEAT
    )

    t_b = measure_mac(
        mac_operation,
        pattern,
        filter_b,
        REPEAT
    )

    print("\n[성능 분석]")
    print(
        f"평균 MAC 시간: "
        f"{(t_a + t_b) / 2:.6f} ms"
    )
    print(
        "연산 횟수: 9 "
        "(필터 1개 기준)"
    )


# ------------------------------------------
# 19. 모드 1
# 사용자 입력 및 저장 패턴 재활용
# ------------------------------------------
def user_input_mode(storage):
    while True:
        print(
            "\n[모드 1: 사용자 입력 / "
            "패턴 재활용]"
        )

        print("1. 직접 입력 (3x3)")
        print(
            "2. 저장된 Cross/X 패턴 사용"
        )
        print(
            "3. 새 패턴 생성 후 사용"
        )
        print("q. 메인 메뉴")

        choice = input(
            "선택: "
        ).strip().lower()

        if choice == "1":
            manual_input_mode()
            return

        if choice == "2":
            label = choose_generated_pattern(
                storage
            )

            if label is not None:
                analyze_generated_pattern(
                    storage,
                    label
                )

            return

        if choice == "3":
            pattern_generator_mode(storage)
            return

        if choice == "q":
            return

        print(
            "1, 2, 3 또는 q를 입력하세요."
        )


# ------------------------------------------
# 20. 기존 크기별 성능 분석
# ------------------------------------------
def performance_analysis():
    print(
        "\n[기본 성능 분석: "
        "Cross 패턴]"
    )

    print(
        f"반복 횟수: {REPEAT}회"
    )

    print(
        f"\n{'크기':<8}"
        f"{'평균(ms)':>14}"
        f"{'원소 수':>12}"
    )

    print("-" * 36)

    for size in SIZES:
        pattern = generate_cross(size)

        average = measure_mac(
            mac_operation,
            pattern,
            pattern,
            REPEAT
        )

        print(
            f"{size}x{size:<5}"
            f"{average:>14.6f}"
            f"{size * size:>12}"
        )

    print(
        "\n시간 복잡도: O(N^2)"
    )


# ------------------------------------------
# 21. 2차원 / 1차원 MAC 성능 비교
# ------------------------------------------
def compare_performance(
    pattern,
    cross_filter,
    x_filter,
    size,
    source
):
    print("\n" + "=" * 56)
    print(
        f"[성능 분석] "
        f"{source} / {size}x{size}"
    )
    print("=" * 56)

    print(
        f"각 방식 {BONUS_REPEAT}회 반복"
    )
    print(
        "배열 변환 시간은 "
        "측정에서 제외"
    )

    print(
        f"\n{'필터':<9}"
        f"{'2차원(ms)':>14}"
        f"{'1차원(ms)':>14}"
        f"{'점수 일치':>12}"
    )

    print("-" * 56)

    for name, filter_data in (
        ("Cross", cross_filter),
        ("X", x_filter)
    ):
        flat_pattern = flatten_matrix(
            pattern
        )

        flat_filter = flatten_matrix(
            filter_data
        )

        score_2d = mac_operation(
            pattern,
            filter_data
        )

        score_1d = mac_operation_flat(
            flat_pattern,
            flat_filter
        )

        matched = (
            abs(score_2d - score_1d)
            < EPSILON
        )

        # 측정 전 사전 실행
        mac_operation(
            pattern,
            filter_data
        )

        mac_operation_flat(
            flat_pattern,
            flat_filter
        )

        # 2차원 MAC 측정
        t2 = measure_mac(
            mac_operation,
            pattern,
            filter_data,
            BONUS_REPEAT
        )

        # 1차원 MAC 측정
        t1 = measure_mac(
            mac_operation_flat,
            flat_pattern,
            flat_filter,
            BONUS_REPEAT
        )

        status = (
            "일치" if matched else "불일치"
        )

        print(
            f"{name:<9}"
            f"{t2:>14.6f}"
            f"{t1:>14.6f}"
            f"{status:>12}"
        )

    print("-" * 56)
    print(
        "두 방식의 시간 복잡도: O(N^2)"
    )
    print(
        "실행 시간은 컴퓨터 환경에 "
        "따라 다릅니다."
    )


# ------------------------------------------
# 22. 보너스 1 성능 분석
# 저장 패턴 재활용
# ------------------------------------------
def bonus_optimization(storage):
    print(
        "\n[보너스 1: MAC 성능 비교]"
    )

    print(
        "1. 기본 패턴 성능 비교"
    )
    print(
        "2. 보너스 2에서 저장한 "
        "패턴 재활용"
    )
    print("q. 메인 메뉴")

    choice = input(
        "선택: "
    ).strip().lower()

    if choice == "1":
        for size in SIZES:
            cross = generate_cross(size)
            x_pattern = generate_x(size)

            compare_performance(
                cross,
                cross,
                x_pattern,
                size,
                "기본 Cross"
            )

    elif choice == "2":
        label = choose_generated_pattern(
            storage
        )

        if label is not None:
            compare_performance(
                storage[label],
                storage["Cross"],
                storage["X"],
                storage["size"],
                f"저장된 {label}"
            )

    elif choice == "q":
        return

    else:
        print("잘못된 선택입니다.")


# ------------------------------------------
# 23. JSON 파일 불러오기
# ------------------------------------------
def load_json():
    path = Path(__file__).resolve().with_name(
        "data.json"
    )

    try:
        with path.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError
    ) as error:
        print(
            f"JSON 파일 오류: {error}"
        )
        return None

    if not isinstance(data, dict):
        print(
            "JSON 최상위 형식 오류"
        )
        return None

    if not isinstance(
        data.get("filters"),
        dict
    ):
        print(
            "filters 객체가 없습니다."
        )
        return None

    if not isinstance(
        data.get("patterns"),
        dict
    ):
        print(
            "patterns 객체가 없습니다."
        )
        return None

    return data


# ------------------------------------------
# 24. JSON 필터 불러오기
# ------------------------------------------
def get_filters(filters, size):
    group = filters.get(
        f"size_{size}"
    )

    if not isinstance(group, dict):
        raise ValueError(
            f"size_{size} 필터가 없습니다."
        )

    normalized = {}

    for name, matrix in group.items():
        label = normalize_label(name)

        if label is None:
            continue

        if label in normalized:
            raise ValueError(
                f"{label} 필터 중복"
            )

        validate_matrix(
            matrix,
            size
        )

        normalized[label] = matrix

    if "Cross" not in normalized:
        raise ValueError(
            "Cross 필터가 없습니다."
        )

    if "X" not in normalized:
        raise ValueError(
            "X 필터가 없습니다."
        )

    return (
        normalized["Cross"],
        normalized["X"]
    )


# ------------------------------------------
# 25. JSON 테스트 케이스 분석
# 모드 2는 UNDECIDED 유지
# ------------------------------------------
def analyze_case(
    case_id,
    case_data,
    filters
):
    match = re.fullmatch(
        r"size_(\d+)_(\d+)",
        case_id
    )

    if match is None:
        raise ValueError(
            "패턴 키 형식 오류"
        )

    size = int(
        match.group(1)
    )

    if size not in (5, 13, 25):
        raise ValueError(
            f"지원하지 않는 크기: {size}"
        )

    if not isinstance(
        case_data,
        dict
    ):
        raise ValueError(
            "패턴 데이터 형식 오류"
        )

    if "input" not in case_data:
        raise ValueError(
            "input 항목 없음"
        )

    if "expected" not in case_data:
        raise ValueError(
            "expected 항목 없음"
        )

    expected = normalize_label(
        case_data["expected"]
    )

    if expected is None:
        raise ValueError(
            "expected 라벨 오류"
        )

    pattern = case_data["input"]

    validate_matrix(
        pattern,
        size
    )

    cross_filter, x_filter = get_filters(
        filters,
        size
    )

    cross_score = mac_operation(
        pattern,
        cross_filter
    )

    x_score = mac_operation(
        pattern,
        x_filter
    )

    result = classify(
        cross_score,
        x_score,
        "Cross",
        "X"
    )

    print(
        f"Cross 점수: {cross_score}"
    )
    print(
        f"X 점수: {x_score}"
    )

    # JSON 분석에서는 내부 판정값 사용
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
            f"예상 {expected}, "
            f"실제 {result}"
        )

    print(
        f"결과: FAIL ({reason})"
    )

    return False, reason


# ------------------------------------------
# 26. JSON 자동 분석 모드
# ------------------------------------------
def json_analysis_mode():
    print(
        "\n[JSON 자동 분석]"
    )

    data = load_json()

    if data is None:
        return

    print(
        "data.json 로드 완료!"
    )

    filters = data["filters"]
    patterns = data["patterns"]

    for size in (5, 13, 25):
        try:
            get_filters(
                filters,
                size
            )

            print(
                f"size_{size} "
                "필터 확인 완료"
            )

        except ValueError as error:
            print(
                f"size_{size} "
                f"필터 오류: {error}"
            )

    passed = 0
    failures = []

    for case_id, case_data in patterns.items():
        print(
            f"\n--- {case_id} ---"
        )

        try:
            success, reason = analyze_case(
                case_id,
                case_data,
                filters
            )

        except (
            ValueError,
            TypeError,
            OverflowError
        ) as error:
            success = False
            reason = str(error)

            print(
                f"결과: FAIL ({reason})"
            )

        if success:
            passed += 1

        else:
            failures.append(
                (case_id, reason)
            )

    performance_analysis()

    print("\n[결과 요약]")
    print(
        f"총 테스트: {len(patterns)}개"
    )
    print(
        f"PASS: {passed}개"
    )
    print(
        f"FAIL: {len(failures)}개"
    )

    if failures:
        print(
            "\n[실패 케이스 목록]"
        )

        for case_id, reason in failures:
            print(
                f"- {case_id}: {reason}"
            )


# ------------------------------------------
# 27. 메인 메뉴
# ------------------------------------------
def show_menu(storage):
    print(
        "\n" + "=" * 48
    )
    print(
        "        Mini NPU Simulator"
    )
    print(
        "=" * 48
    )

    print(
        "1. 사용자 입력 / 저장 패턴 재활용"
    )
    print(
        "2. data.json 자동 분석"
    )
    print(
        "3. 성능 분석 / 저장 패턴 재활용"
    )
    print(
        "4. Cross / X 패턴 생성 및 저장"
    )
    print(
        "0. 종료"
    )

    if storage:
        size = storage["size"]

        print(
            f"\n현재 저장된 패턴: "
            f"{size}x{size}"
        )

    print()


# ------------------------------------------
# 28. 메인 함수
# ------------------------------------------
def main():
    # 프로그램 실행 중 패턴 저장
    generated_patterns = {}

    while True:
        show_menu(
            generated_patterns
        )

        choice = input(
            "선택: "
        ).strip()

        if choice == "1":
            user_input_mode(
                generated_patterns
            )

        elif choice == "2":
            json_analysis_mode()

        elif choice == "3":
            bonus_optimization(
                generated_patterns
            )

        elif choice == "4":
            pattern_generator_mode(
                generated_patterns
            )

        elif choice == "0":
            print(
                "프로그램을 종료합니다."
            )
            break

        else:
            print(
                "0, 1, 2, 3, 4 중 "
                "선택하세요."
            )


# ------------------------------------------
# 프로그램 시작
# ------------------------------------------
if __name__ == "__main__":
    try:
        main()

    except (
        KeyboardInterrupt,
        EOFError
    ):
        print(
            "\n프로그램을 종료합니다."
        )
