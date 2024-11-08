# Explorando las capacidades de GPT-2 para generar comentarios humorísticos

## Introducción
En este proyecto exploraremos las capacidades de GPT-2 para generar comentarios 
humoristicos en español. Para ello utilizaremos la tecnica de fine-tuning, que 
consiste en entrenar el modelo con un dataset específico para que pueda generar 
texto con un estilo particular. 

Los resultados obtenidos durante el entrenamoento no fueron los esperados, 
por lo que concluimos que GPT-2 no esta preparado para entender un concepto tan 
abstracto o subjetivo como lo es el humor.

En las siguientes secciones se presentaran detalles del modelo utilizado, la 
base de datos que construimos, la metodología y parámetros que utilizamos para
entrenar el modelo, luego una evaluación de los resultados obtenidos y finalmente
conclusiones y trabajo futuro. Y como anexo se presentaran las complicaciones
encontradas durante el desarrollo del proyecto.

## Modelo

El modelo utilizado es [GPT2-medium](https://huggingface.co/DeepESP/gpt2-spanish-medium) 
que es un modelo de generacion de lenguaje entreneado desde cero con  11,5GB de 
textos en español de los cuales 3.5 corresponden a articulos de Wikipedia y 8GB 
a libros de narrativa, cuentos, poesias, ensayos y divulgación. Los datos usan 
tokenizador Byte Pair Encoding (BPE), los parámetros utilizados son los mismos 
que los de la version mediana del modelo OpenAI GPT-2 original.

En la siguiente imagen se puede la arquitectura del modelo, que consiste en 
cargar la base de datos de hugginface, luego el modelo base que describirmos 
anteriormente. Luego realizar el fine-tunning, una vez realizado esto 
el usuario puede ingresar una pregunta y el modelo fine tuneado le devolvera
por medio de un bot de telegram una respuesta graciosa, la cual podrá ser 
evaluada por el usuario con un like o dislike.

<figure>
    <img src='./pictures/arq.jpg' alt="Descripción de la imagen">
</figure>

En las siguentes secciones se darán detalles mas profundos de cada parte de la
arquitectura.

### Base de datos

Dada la gran variedad de estructuras de chistes que existen, decidimos limitar 
nuestro experimento a solo un tipo de chistes. Es por esto que decidimos utilizar
los del tipo pregunta y respuesta, como por ejemplo:

```
P: ¿De qué murió Bob Marley?
R: De un porrazo.
```
Como no encontramos datos en español con este formato, decidimos construir nuestra
propia base de datos, usando una conbinación de las disponibles en Huggingface 
y aplicando un filtro para quedarnos solo con los chistes del tipo pregunta y
respuesta ([1](https://huggingface.co/datasets/ysharma/short_jokes),
[2](https://huggingface.co/datasets/xaviviro/chistes_eugenio),
[3](https://huggingface.co/datasets/Danielbrdz/Barcenas-HumorNegro),
[4](https://huggingface.co/datasets/mrm8488/CHISTES_spanish_jokes)). Al combinar 
estos datasets obtuvimos de unos 700 chistes, lo que nos parecio poco, por lo que
decidimos hacer un web scraping de algunas paginas aleatorias para poder lograr 
un total de 1.732 chistes. 

A su vez, a cada elemento de la [base de datos](https://huggingface.co/datasets/kevmansilla/jokes_spanish_tm) decidimos agregarles unos tags que ayuden al modelo 
a entender la estructura del chiste y poder generar respuestas más acertadas. 
Como por ejemplo:
```
<START>[QUESTION] ¿De qué murió Bob Marley? [ANSWER] De un porrazo. <END>
```
Donde `<START>` y `<END>` son los tokens de inicio y fin de texto, `[QUESTION]` y 
`[ANSWER]` son los tags que indican el tipo de texto que sigue y precede. Estos 
seran de gran ayuda al momento de entrenar el modelo y generar respuestar acordes.

### Metodología y entrenamiento

Para entrenar el modelo utilizamos la libreria `transformers` de Huggingface,
que nos permite hacer fine-tuning de modelos pre-entrenados. Para ello, primero
cargamos el modelo pre-entrenado y luego lo entrenamos con nuestra base de datos.

Antes de iniciar el entrenamiento separamos la base de datos en un set de entrenamiento y otro de validación, con un 70% y 30% respectivamente. Luego, 
tokenizamos los textos y los convertimos en tensores para poder alimentar al modelo.

Para entrenar el modelo utilizamos la metodologia de batch size, que consiste en 
entrenar el modelo con un conjunto de datos de tamaño fijo, para luego actualizar
los pesos del modelo (desarrollar un poco mas).

Los parametros utilizados para el entrenamiento fueron los siguientes:
``` overwrite_output_dir=True,
    num_train_epochs=12,
    learning_rate=1e-6,
    per_device_eval_batch_size=8,
    per_device_train_batch_size=8,
    weight_decay=0.01,
    eval_strategy='epoch',  # Cambiado de evaluation_strategy a eval_strategy
    save_strategy='epoch',  # Guardamos al final de cada época
    load_best_model_at_end=True,  # Cargamos el mejor modelo al final
    disable_tqdm=False,
    logging_steps=162,
    save_total_limit=2,
    # Utilizamos eval_loss como métrica de referencia
    metric_for_best_model="eval_loss",
    greater_is_better=False  # Indica que buscamos minimizar eval_loss
```
Y luego utilizamos la función `Trainer` de la libreria `transformers` para entrenar
el modelo. Agregamos early stopping de 3 épocas para evitar el sobreajuste, es 
decir, que cuando la métrica de evaluación no mejora en 3 épocas seguidas, se
detiene el entrenamiento y se guarda el mejor modelo.

El modelo fue entrenado usando computo del [CCAD](https://ccad.unc.edu.ar/) de la UNC, usando la computadora [Jupyter](https://wiki.ccad.unc.edu.ar/infra/computadoras.html)

## Evaluación

El principal problema que presenta este trabajo es la evalación del modelo, debido a que el humor es un tema muy dibjetivo por lo que una métrica de las 
tradicionales no son muy informativas. Es por ello que se decidio implementar un bot de telegram que permita a los usuarios evaluar las respuestas generadas
por el modelo.

El bot, utilizando el modelo entrenado respondera con el texto generado y 
luego los usuarios podrán calificar con like y dislike si el chiste les gusto 
o no. como por ejemplo en la siguiente imagen:


<figure>
    <img src='./pictures/bot.png' alt="Descripción de la imagen">
</figure>

Esto nos fue de gran utilidad para poder evaluar el modelo. Por lo que podemos 
decir que el bot fue capaz de responder un 88.14% de las preguntas que se 
le realizaron y de estas el 25.0% fueron calificadas como graciosas.

## Conclusiones

## Trabajo futuro

## Anexo: Complicaciones encontradas durante el desarrollo del proyecto

Nuestra idea inicial, era generar comentarios humoristicos a partir de una 
lista de tópicos como por ejemplo "futbol", "política", "religión", etc. Y que 
el modelo pudiera generar comentarios graciosos a partir de estos temas. Para 
esto entrenamos el modelo con una una 
[base de datos](https://huggingface.co/datasets/mrm8488/CHISTES_spanish_jokes)
en español de huggingface de 2419 chistes. 

Como punto de partida, realizamos un análisis exploratorio de la base para 
identificar atributos como el largo de los chistes y determinar cuál categoria 
predominaba, ya que los datos venían pre-clasificados. Sin embargo, no resultó 
de mucha utilidad ya que gran cantidad de l contenido estaban incluidas en una 
categoria denominada 'otros' que no aportaba mucha información.

Por esta razón, complementamos el análisis con distintas técnicas no supervisadas de topic modelling como lo es clustering y LDA. Luego de analizar los resultados, decidimos quedarnos con el LDA ya que en los resultados obtenidos por clustering las palabras de cada grupo no tenían mucha relación entre sí, en cambio en LDA si se podría ver un hilo conductor. 

Luego de esto, entrenamos el modelo, lo cual también trajo varios inconvenientes. El primero fue que nos dimos cuenta que al entrenarlo durante muchas iteraciones se produce un overfitting. Entonces para solucionar esto usamos early stopping de modo que el entrenamiento se detuviera automáticamente si el validation loss no mejoraba durante varias épocas consecutivas, permitiendo encontrar un punto óptimo. Luego de esto, usamos el modelo entrenado para generar los chistes y nos encontramos con el problema de que producía texto sin sentido y muy extenso lo que dificulta encontrar un hilo conductor en el chiste, como lo siguiente:

```
Chiste generado: Había una vez un hombre a caballo en un carreta. ¿Estaba montado por la mañana?
- Sí, pero no estaba de humo, al contrario, me dijo que estaba cansado.
- Entonces, ¿por qué no me lo dijiste?
- ¿Por qué no?
- Porque si yo no lo hubiera dicho lo hubiera hecho.
- Pero si lo hubiera dicho yo no lo hubiera hecho.
- ¿Por qué no lo has hecho?¿Por qué no has hecho? De todos
```

Para abordar este problema, planteamos dos enfoques. El primero fue utilizar n-gramas y, el segundo, emplear una base de datos más grande, que debido a la limitada disponibilidad de los datos en español, optamos por probar con una en inglés.

En la primera opción, decidimos usar 2-gramas para aprovechar ventajas como la reducción de ambigüedad, la limitación del contexto, la mejora de fluidez y la captura de dependencias locales. Si bien esta técnica mejoró la coherencia del texto, los resultados no fueron satisfactorios en términos de la longitud de los chistes generados, tampoco se logró mejorar el desempeño humorístico. A continuación un ejemplo:

```
Chiste generado: Un perro entra a un bar y pide una bebida.
-¿Qué te trae por aquí? - pregunta el camarero al otro lado de la barra, en tono amenazante. El hombre se queda pensativo unos instantes antes de responder:
-¿Qué qué traía?
```
La segunda opción arrojó los mismos resultados que el enfoque anterior, lo que nos llevó a la conclusión de que el problema no radicaba ni en la cantidad de chistes disponibles ni en cómo estos eran procesados. Sino que era un inconveniente de la estructura de los mismos, ya que ambas bases tenían chistes con estructuras muy diversas, lo que dificulta el modelo de capturar patrones. 

Por estas razones, decidimos cambiar el enfoque del trabajo de generación de 
comentarios humotisticos por medio de tópicos a generarlos por medio de una 
pregunta y esto condujo a los resultados presentados en las secciones
anteriores.
