## Установка

- Скачать драйвер: https://googlechromelabs.github.io/chrome-for-testing/#stable

## Суть

### Сбор датасетов

1. Парсятся данные количества заказов такси с определенной точки в течении дня за несколько дней с карты на [сайте]().
2. Парсятся данные погоды в течении дня за несколько дней с [сайта]().
3. Собирается итоговый датасет

Устройство датасета

| Назение      | Описание                                                                       |
|--------------|--------------------------------------------------------------------------------|
| hex_id       | Id участка карты                                                               |
| date         | Дата                                                                           |
| time         | Время                                                                          |
| rides_count  | Количество поездок такси, заказанных в эту дату и время из этого участка карты |
| weather_data | Температура, влажность, скорость ветра                                         |
| population   | ДОПИСАТЬ                                                                       |

Количество строк: ДОПИСАТЬ

Датасет: [ссылка]()

### Обучение модели

ДОПИСАТЬ

## Команда 

1. Макс Кудряшов: [GitHub]() | [Telegram]()
2. ДОПИСАТЬ