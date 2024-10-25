import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from bd import *


# Cargar el modelo y tokenizer
model = AutoModelForCausalLM.from_pretrained(
    'kevmansilla/generate_jokes_question_answer'
)
tokenizer = AutoTokenizer.from_pretrained(
    'kevmansilla/generate_jokes_question_answer'
)


def generate_short_joke(prompt, max_length=50, temperature=0.3, top_k=25, top_p=0.9) -> str:
    '''
    Genera un chiste breve basado en el prompt proporcionado.
    '''

    # Tokenización del prompt con atención explícita
    inputs = tokenizer(prompt, return_tensors='pt', padding=True)
    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    # Generar el chiste usando atención explícita
    output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=max_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        num_return_sequences=1,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.convert_tokens_to_ids('<END>')
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Maneja los mensajes recibidos.
    '''

    chat_id = update.message.chat_id  # Obtener el ID del chat
    prompt = f'<START>[QUESTION]{update.message.text}'  # Formatear el prompt
    joke = generate_short_joke(prompt)  # Generar el chiste

    # Guardar el chiste en la base de datos
    save_joke(chat_id, joke)

    # Extraer el texto después de [ANSWER] y eliminar todos los <END> al final
    match = re.search(r'\[ANSWER\](.*?)(?:<END>)*$', joke, re.DOTALL)

    # Si no hay coincidencia, usa el chiste completo
    final_joke = match.group(1).strip() if match else joke

    # borro todo lo que esta despues del primer <END>
    final_joke = re.sub(r'<END>.*', '', final_joke)

    # Crear los botones de reacciones
    keyboard = [
        [
            InlineKeyboardButton('👍 Me gusta', callback_data='like'),
            InlineKeyboardButton('👎 No me gusta', callback_data='dislike')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar el chiste con los botones de reacción
    await update.message.reply_text(final_joke, reply_markup=reply_markup)


async def handle_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Maneja la reacción del usuario (like/dislike).
    '''

    query = update.callback_query
    chat_id = query.message.chat_id  # Obtener el ID del chat
    reaction = query.data  # Obtener la reacción ('like' o 'dislike')

    # Confirmar la interacción del usuario
    await query.answer()

    # Guardar la reacción en la base de datos
    update_reaction(chat_id, reaction)

    # Responder al usuario con un mensaje adecuado
    if reaction == 'like':
        response = '¡Gracias por el 👍!'
    else:
        response = '¡Lo intentaré mejor la próxima vez! 👎'

    # Eliminar los botones y enviar la respuesta
    await query.edit_message_reply_markup(None)
    await query.message.reply_text(response)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Maneja el comando /start y envía un mensaje de bienvenida si el usuario no está suscrito.
    '''

    chat_id = update.message.chat_id

    if not is_user_subscribed(chat_id):
        # Si el usuario no está suscrito, lo añadimos y enviamos un mensaje de bienvenida
        add_user(chat_id)
        print('Nuevo usuario:', chat_id)
        await update.message.reply_text(
            '¡Bienvenido al bot de chistes! 🎉 Espero hacerte reír mucho.'
        )
    else:
        await update.message.reply_text('¡Ya estás suscrito! 😊 Escribe algo para recibir un chiste.')


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Maneja la desuscripción del usuario.
    '''

    chat_id = update.message.chat_id

    if is_user_subscribed(chat_id):
        remove_user(chat_id)
        print('Usuario eliminado:', chat_id)
        await update.message.reply_text(
            '¡Lamentamos que te vayas! 😢 Esperamos verte de nuevo pronto.'
        )
    else:
        await update.message.reply_text('No estabas suscrito. Si quieres suscribirte, usa /start.')


def main():
    create_database()
    TOKEN = '7696528566:AAEiUzTjBnM6es0yp6R040oMq4wZCEZYh54'

    app = ApplicationBuilder().token(TOKEN).build()

    # Manejadores de comandos y mensajes
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('unsubscribe', unsubscribe))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_reaction))

    print('Bot iniciado...')
    app.run_polling()


if __name__ == '__main__':
    main()
