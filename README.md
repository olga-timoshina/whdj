
# QA Портфолио - Тимошина Ольга 
Здравствуйте! Меня зовут Тимошина Ольга, я начинающий QA Engineer.
В этом портфолио представлен пример моего тестирования веб - системы складского учёта,которые показывают мой подход к проверке фукциональности и оформлению документации. 

## Контакты
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Тимошина Ольга — QA Engineer</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            padding: 24px 16px;
            background: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            color: #1f2328;
            line-height: 1.5;
        }

        .container {
            max-width: 860px;
            margin: 0 auto;
        }

        h1 {
            font-size: 24px;
            margin: 0 0 4px;
        }

        .subtitle {
            color: #656d76;
            font-size: 14px;
            margin: 0 0 20px;
        }

        /* ---------- Таблица контактов ---------- */
        table.contacts {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        table.contacts thead th {
            background: #f6f8fa;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
            color: #57606a;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            padding: 10px 16px;
            border-bottom: 1px solid #d0d7de;
        }

        table.contacts th:first-child,
        table.contacts td:first-child {
            width: 40%;
        }

        table.contacts td {
            padding: 12px 16px;
            border-bottom: 1px solid #eaeef2;
            font-size: 14px;
            vertical-align: middle;
        }

        table.contacts tr:last-child td {
            border-bottom: none;
        }

        table.contacts tr:hover td {
            background: #f6f8fa;
        }

        table.contacts a {
            color: #0969da;
            text-decoration: none;
            word-break: break-word;
        }

        table.contacts a:hover {
            text-decoration: underline;
        }

        .icon {
            display: inline-block;
            width: 20px;
            margin-right: 8px;
            text-align: center;
        }

        /* ---------- Блок с PDF ---------- */
        .pdf-wrapper {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        .pdf-wrapper iframe {
            display: block;
            width: 100%;
            height: 80vh;
            min-height: 500px;
            border: none;
        }

        @media (max-width: 600px) {
            table.contacts th:first-child,
            table.contacts td:first-child {
                width: 45%;
            }
            .pdf-wrapper iframe { height: 70vh; }
        }
    </style>
</head>
<body>
    <div class="container">

        <h1>Тимошина Ольга</h1>
        <p class="subtitle">QA Engineer · Ручное тестирование · API · Network</p>

        <!-- ---------- Таблица контактов ---------- -->
        <table class="contacts">
            <thead>
                <tr>
                    <th>Канал</th>
                    <th>Ссылка</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="icon">📄</span>Резюме (PDF)</td>
                    <td>
                        <a href="https://olga-timoshina.github.io/whdj/docs/Timoshina_Olga_QA_CV.pdf" target="_blank" rel="noopener">Открыть PDF</a>
                    </td>
                </tr>
                <tr>
                    <td><span class="icon">📄</span>Резюме (HH.ru)</td>
                    <td>
                        <a href="https://hh.ru/resume/be2f9113ff10ad8de20039ed1f44524f624179" target="_blank" rel="noopener">hh.ru/resume/be2f9113…</a>
                    </td>
                </tr>
                <tr>
                    <td><span class="icon">✈️</span>Telegram</td>
                    <td>
                        <a href="https://t.me/OlgaTimoshina" target="_blank" rel="noopener">@OlgaTimoshina</a>
                    </td>
                </tr>
                <tr>
                    <td><span class="icon">✉️</span>Email</td>
                    <td>
                        <a href="mailto:olga31172@yandex.ru">olga31172@yandex.ru</a>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- ---------- PDF ---------- -->
        <div class="pdf-wrapper">
            <iframe src="https://olga-timoshina.github.io/whdj/docs/Timoshina_Olga_QA_CV.pdf" title="Резюме Тимошина Ольга"></iframe>
        </div>

    </div>
</body>
</html>

| Канал | Ссылка |
|-------|--------|

| 📄 Резюме (HH.ru) | https://hh.ru/resume/be2f9113ff10ad8de20039ed1f44524f624179 |
| ✈️ Telegram | https://t.me/OlgaTimoshina |
| ✉️ Email | olga31172@yandex.ru |


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
