ZAP-скан

upravlenie_activami.py  - добавить/ удалить актив уязвимой машины для сканирования
zap_spider_only.py - проводит анализ спайдером, выводит все найденные уязвимости в командную строку, и завершает и удаляет образ
zap_final_scan_without_docker.py - проводит полный анализ в активном режиме, выводит все найденные уязвимости в командную строку. подробности выводит в текстовый файл
Я завершал и удалял образ так как как два сканирования вызывали проблемы с завершением сессии, если запускаешь сканы через докер. решил их разделить. В final_scan мы не должны запускать скан через докер . Нужно запустить сам зап у себя на устройстве, иначе не хватит времени сессии на завершение сканирования
Установка архива wget https://github.com/zaproxy/zaproxy/releases/download/v2.16.1/ZAP_2.16.1_Linix.tar.gz
tar -xzf ZAP_2.16.1_Linix.tar.gz
./zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true


Для общего протокола выпишу сюда команды запуска для обычного спайдера через докер:
Создаём папку, перемещаемcя в неё по cd.
с помощью nano создаём питон файлы
chmod +x file.py - наделяем нужными правами на выполнение
Запускаем контейнер docker run -d --name zap-api --network host zaproxy/zap-stable zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
Скачиваем и запускаем контейнер juiceshop:
docker pull bkimminich/juice-shop
docker run -d -p 3000:3000 --name juice-shop bkimminich/juice-shop
(P.S. если для теста хотите начать сканирование сайта в UI и два докер образа не в одной сети используйте ссылку 
http://host.docker.internal:3000 за место локал хоста, а если хотите обратится по curl чтобы проверить версию используем
docker exec zap-api curl -s http://localhost:8080/JSON/core/view/version)
