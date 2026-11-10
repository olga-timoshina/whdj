
# QA Портфолио - Тимошина Ольга 
Здравствуйте! Меня зовут Тимошина Ольга, я начинающий QA Engineer.
В этом портфолио представлен пример моего тестирования веб - системы складского учёта,которые показывают мой подход к проверке фукциональности и оформлению документации. 

## Контакты
[![Resume](https://img.shields.io/badge/Резюме-HH.ru-red?logo=internetexplorer&logoColor=white)](https://hh.ru/resume/db9433f0ff0fc784b20039ed1f514f31797642)
[![Telegram](https://img.shields.io/badge/Telegram-@OlgaTimoshina-26A5E4?logo=telegram&logoColor=white)](https://t.me/OlgaTimoshina)
[![Email](https://img.shields.io/badge/Email-olga31172@yandex.ru-EA4335?logo=gmail&logoColor=white)](mailto:olga31172@yandex.ru)
Резюме https://hh.ru/resume/db9433f0ff0fc784b20039ed1f514f31797642


# Warehouse QA — Портфолио тест-кейсов

Коллекция тест-кейсов для веб-приложения «Складская система учёта».

![Tests](https://img.shields.io/badge/test%20cases-23-blue)
![Browsers](https://img.shields.io/badge/browsers-Chrome%20%7C%20Firefox%20%7C%20Safari-orange)
![Network](https://img.shields.io/badge/tool-Chrome%20DevTools-green)

**SUT:** https://warehouse-django-nmp9.onrender.com/

## 📁 Содержимое

| Файл | Раздел | Кейсов |
|------|--------|--------|
| [cross-browser.md](test-cases/cross-browser.md) | Кросс-браузерность (UI + Functional) | 3 |
| [network.md](test-cases/network.md) | Сетевые запросы (DevTools → Network) | 10 |
| [products.md](test-cases/products.md) | Справочник «Товары» | 10 |
| [environment.md](docs/environment.md) | Окружение и предусловия | — |

## 🛠 Что демонстрируют кейсы

- Cross-browser тестирование (Blink / Gecko / WebKit)
- Анализ HTTP-трафика: методы, статусы, заголовки, тайминги
- Позитивные / негативные / boundary-сценарии
- Проверка безопасности (HTTPS, mixed content, отсутствие утечек в ответах)

## 👤 Автор

Ваше Имя — [LinkedIn](#) · [Telegram](#)

## 1. Цель тестирования

Проверка корректности основных функций системы складского учета:
- работа со справочниками;
- оформление складских операций;
- корректный пересчет остатков;
- запрет отрицательных остатков;
- фиксация операций в журнале движений;
- сохранение целостности данных.

## 2. Чек-лист

### Справочники
- [ ] Создание товара
- [ ] Редактирование товара
- [ ] Просмотр товара
- [ ] Удаление/деактивация товара
- [ ] Создание склада
- [ ] Редактирование склада
- [ ] Создание контрагента

### Складские операции
- [ ] Оформление прихода товара
- [ ] Оформление расхода товара
- [ ] Перемещение товара между складами
- [ ] Проверка пересчета остатков после операции
- [ ] Проверка запрета отрицательного остатка
- [ ] Проверка записи операции в журнал движений
