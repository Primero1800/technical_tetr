def normalize_intervals(intervals: list[int]) -> list[tuple]:
    """
    Дополнительная функция нормализации в связи с наличием второго набора таймстампов,
    немного противоречащих логике, но не противоречащих условию
    """
    pairs = sorted(
        [(intervals[i], intervals[i + 1]) for i in range(0, len(intervals), 2)], key=lambda x: x[0]
    )
    merged = []
    for pair in pairs:
        if not merged:
            merged.append(pair)
        else:
            last = merged[-1]
            if pair[0] <= last[1]:
                merged[-1] = (last[0], max(last[1], pair[1]))
            else:
                merged.append(pair)
    return merged


def intersect_intervals(pis: list[tuple], tis: list[tuple]) -> list[tuple]:
    """
    Находим пересечение двух списков интервалов.
    Возвращает список туплов пересечения.
    """
    result = []
    for p in pis:
        for t in tis:
            if p[0] >= t[1] or t[0] >= p[1]:
                continue
            result.append((
                max(p[0], t[0]), min(p[1], t[1])
            ))
    return result


def normalize_by_lesson(intervals: list[tuple], norm: list[int]):
    """Нормализуем результат по периоду урока"""
    result = []
    for interval in intervals:
        if interval[0] >= norm[1] or norm[0] >= interval[1]:
            continue
        result.append(
            min(interval[1], norm[1]) - max(interval[0], norm[0])
        )
    return result


def appearance(intervals: dict[str, list[int]]) -> int:
    combined = intersect_intervals(
        normalize_intervals(intervals["pupil"]),
        normalize_intervals(intervals['tutor'])
    )
    return sum(normalize_by_lesson(combined, intervals["lesson"]))


tests = [
    {'intervals': {'lesson': [1594663200, 1594666800],
                   'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
                   'tutor': [1594663290, 1594663430, 1594663443, 1594666473]},
     'answer': 3117
     },
    {'intervals': {'lesson': [1594702800, 1594706400],
                   'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564,
                             1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096,
                             1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500,
                             1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
                   'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463]},
     'answer': 3577
     },
    {'intervals': {'lesson': [1594692000, 1594695600],
                   'pupil': [1594692033, 1594696347],
                   'tutor': [1594692017, 1594692066, 1594692068, 1594696341]},
     'answer': 3565
     },
]


if __name__ == '__main__':
    for i, test in enumerate(tests):
        test_answer = appearance(test['intervals'])
        assert test_answer == test['answer'], f'Error on test case {i}, got {test_answer}, expected {test["answer"]}'
