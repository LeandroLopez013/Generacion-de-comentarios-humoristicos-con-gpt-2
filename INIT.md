# text-mining

## Iniciar entorno virtual
```
python3 -m venv env
source env/bin/activate
```
## Instalar paquetes necesarios
```
pip3 install -r requirements.txt
``` 
## Actualizar Requeriements

Primero instalar
```
pip3 install pipreqsnb
```

Luego
```
./generate_requirements.sh *.ipynb
```

## Correr Bot de Telegram

[link al bot de telegram](https://t.me/gen_tm_bot)
```
cd bot/
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 bot.py
```