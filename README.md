## Установка

- Скачать драйвер: https://googlechromelabs.github.io/chrome-for-testing/#stable

## To do

- [x] Добавить проверку на то, что уже было спаршено
- [ ] Добавить сохранение таблиц в один csv
- [x] Убрать time.sleep() и добавить проверку загрузилась ли страница полностью
- [ ] Добавить сохранение того, что не получилось спарсить
- [x] Если загрузка слишком долгая, то ниче не делать

## Станции

| Назание                         | Индекс ближайшего здания | Координаты           |
|---------------------------------|--------------------------|----------------------|
| Vnukovo Intl Airport Station    | 119027                   |                      |
| Arbat Station                   | 119002                   | 55.747616, 37.583140 |
| Khamovniki (IMOSCO2)            | 119048                   | 55.729235, 37.571758 |
| Izmaylovo (IMOSCO147)           | 197720                   | 60.194343, 29.700522 |
| Dmitrovsky (IMOSCO140)          | 127247                   | 55.879990, 37.536454 |
| Stations Zyablikovo (IMOSCO87)  | 115580                   | 55.618995, 37.745933 |
| Filevsky Park (IMOSCOW274)      | 121096                   | 55.736154, 37.490604 |
| Stations Krylatskoe (IMOSCO132) | 121614                   | 55.760201, 37.416476 |
| Nagornyy (IMOSCO124)            | 117638                   | 55.667188, 37.614051 |
| Nagatinsky zaton (IMOSCO32)     | 115142                   | 55.674600, 37.689168 |

- Vnukovo Intl Airport Station

## План

1. Для каждого zip_code получить станцию (через парсинг одной даты)
2. Для каждого зип кода получить погоду
   3. Получаю данные для одного зип кода
   4. Записываю эти данные для всех остальных зип кодов с этой станцией