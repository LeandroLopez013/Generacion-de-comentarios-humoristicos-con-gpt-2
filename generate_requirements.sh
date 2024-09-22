#!/bin/bash

# Verifica si el directorio y archivos .ipynb existen
if [ $# -eq 0 ]; then
    echo "Uso: $0 archivo1.ipynb archivo2.ipynb ..."
    exit 1
fi

# Activa el entorno virtual
echo "Activando entorno virtual..."
source env/bin/activate

# Archivo de salida combinado
FINAL_OUTPUT="./requirements.txt"

# Crea o limpia el archivo de salida combinado
> $FINAL_OUTPUT

# Ejecuta pipreqsnb para cada archivo .ipynb
for notebook in "$@"; do
    # Extrae el nombre del archivo sin la extensión
    base_name=$(basename "$notebook" .ipynb)
    
    # Archivo de salida basado en el nombre del notebook
    TEMP_OUTPUT="./${base_name}_requirements.txt"
    
    # Crea o limpia el archivo de salida temporal
    > $TEMP_OUTPUT
    
    echo "Generando requisitos para $notebook..."
    pipreqsnb --savepath $TEMP_OUTPUT $notebook

    # Verifica si se agregaron dependencias
    if [ -s $TEMP_OUTPUT ]; then
        echo "Requisitos generados para $notebook en $TEMP_OUTPUT."
        # Agrega el contenido al archivo final
        cat $TEMP_OUTPUT >> $FINAL_OUTPUT
    else
        echo "No se encontraron requisitos para $notebook."
        rm $TEMP_OUTPUT  # Elimina el archivo si está vacío
    fi
done

# Elimina archivos temporales que se generaron
rm -f ./*_requirements.txt

echo "Requisitos combinados en $FINAL_OUTPUT."

