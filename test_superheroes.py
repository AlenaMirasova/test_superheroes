import pytest
import requests

# Функция по поиску самого высокого супергероя по полу и наличию работы
def get_tallest_hero_by_gender_and_work(gender: str, has_work: bool):
    """
    :param gender: Пол ('Male' или 'Female', регистр не имеет значения)
    :param has_work: True — работа есть, False — нет
    :return: Словарь с данными героя или None
    """
    url = "https://akabab.github.io/superhero-api/api/all.json"
    response = requests.get(url)
    response.raise_for_status()
    heroes_data = response.json()

    gender = gender.lower()
    filtered = []

    for hero in heroes_data:
        hero_gender = hero.get("appearance", {}).get("gender", "").lower()
        if hero_gender != gender:
            continue

        work = hero.get("work", {}).get("occupation", "")
        if bool(work and work.strip() != "-") != has_work:
            continue

        height_cm = hero.get("appearance", {}).get("height", [None, "0"])[1]
        try:
            height_val = int(height_cm.replace(" cm", ""))
        except ValueError:
            continue

        hero["_height_cm"] = height_val
        filtered.append(hero)

    if not filtered:
        return None

    return max(filtered, key=lambda h: h["_height_cm"])


#  Параметризованные тесты
@pytest.mark.parametrize("gender, has_work", [
    ("Male", True),
    ("Male", False),
    ("Female", True),
    ("Female", False),
])
def test_get_tallest_heroes(gender, has_work):
    hero = get_tallest_hero_by_gender_and_work(gender, has_work)
    assert hero is None or isinstance(hero, dict)

    if hero:
        assert "name" in hero
        assert "_height_cm" in hero
        assert isinstance(hero["_height_cm"], int)
        assert hero.get("appearance", {}).get("gender", "").lower() == gender.lower()

        if has_work:
            assert hero.get("work", {}).get("occupation", "").strip() != "-"
        else:
            assert hero.get("work", {}).get("occupation", "").strip() in ["", "-"]


# Тест на несуществующий пол
def test_get_tallest_nonexistent_gender():
    result = get_tallest_hero_by_gender_and_work("Alien", True)
    assert result is None

# Тест на чувствительность к регистру
def test_gender_case_insensitivity():
    hero_upper = get_tallest_hero_by_gender_and_work("Male", True)
    hero_lower = get_tallest_hero_by_gender_and_work("male", True)

    assert hero_upper is not None and hero_lower is not None
    assert hero_upper["name"] == hero_lower["name"]
    assert hero_upper["_height_cm"] == hero_lower["_height_cm"]

# Тест на успешный статус ответа (200 OK)
def test_api_status_code():
    url = "https://akabab.github.io/superhero-api/api/all.json"
    response = requests.get(url)
    assert response.status_code == 200

# Тест на некорректный URL, который приведет к ошибке 
def test_api_bad_status_code():
    url = "https://akabab.github.io/superhero-api/api/nonexistent.json"
    response = requests.get(url)
    assert response.status_code != 200, f"Expected a status code different from 200, but got {response.status_code}"
    assert 400 <= response.status_code < 600, f"Expected status code between 400 and 600, but got {response.status_code}"