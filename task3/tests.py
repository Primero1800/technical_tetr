import pytest

from solution import normalize_intervals, intersect_intervals, normalize_by_lesson, appearance


@pytest.mark.asyncio
async def test_normalize_intervals_merge_overlapping():
    intervals = [1, 5, 2, 6, 8, 10]
    normalized = normalize_intervals(intervals)
    assert normalized == [(1, 6), (8, 10)]


@pytest.mark.asyncio
async def test_normalize_intervals_non_overlapping():
    intervals = [1, 3, 5, 7]
    normalized = normalize_intervals(intervals)
    assert normalized == [(1, 3), (5, 7)]


@pytest.mark.asyncio
async def test_intersect_intervals_simple():
    pis = [(1, 5), (6, 10)]
    tis = [(3, 7), (8, 12)]
    result = intersect_intervals(pis, tis)
    expected = [(3, 5), (6, 7), (8, 10)]
    assert sorted(result) == sorted(expected)


@pytest.mark.asyncio
async def test_intersect_intervals_no_overlap():
    pis = [(1, 2), (4, 5)]
    tis = [(3, 4), (6, 7)]
    result = intersect_intervals(pis, tis)
    assert result == []


@pytest.mark.asyncio
async def test_normalize_by_lesson_partial_overlap():
    intervals = [(1594663340, 1594663389), (1594663390, 1594663395)]
    norm = [1594663200, 1594666800]
    result = normalize_by_lesson(intervals, norm)
    assert sum(result) == (1594663389 - 1594663340) + (1594663395 - 1594663390)


@pytest.mark.asyncio
async def test_appearance_with_sample_data():
    test_data = {
        'lesson': [1594663200, 1594666800],
        'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
        'tutor': [1594663290, 1594663430, 1594663443, 1594666473],
    }
    result = appearance(test_data)
    assert result == 3117


@pytest.mark.asyncio
async def test_appearance_with_another_sample():
    test_data = {
        'lesson': [1594702800, 1594706400],
        'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564,
                  1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096,
                  1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500,
                  1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
        'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463],
    }
    result = appearance(test_data)
    assert result == 3577


@pytest.mark.asyncio
async def test_appearance_with_non_overlapping_intervals():
    """Непересекающиеся интервалы"""
    intervals = {
        'lesson': [1000, 2000],
        'pupil': [3000, 4000],
        'tutor': [5000, 6000],
    }
    assert appearance(intervals) == 0


@pytest.mark.asyncio
async def test_empty_intervals():
    intervals = {
        'lesson': [1000, 2000],
        'pupil': [],
        'tutor': [],
    }
    assert appearance(intervals) == 0


@pytest.mark.asyncio
async def test_single_point_intervals():
    intervals = {
        'lesson': [1000, 2000],
        'pupil': [1500, 1500],
        'tutor': [1500, 1500],
    }
    assert appearance(intervals) == 0
