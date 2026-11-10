import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# מבנה נתונים וזיכרון פנימי של הבוט
car_state = {
    "driver": "אפרת",       # נהג/ת: אפרת או דורון
    "front": "דורון",        # מושב ליד הנהג: דורון / אפרת / אין
    "rear_left": "עלמה",    # מאחורי הנהג (מאחורי אפרת)
    "rear_right": "יואב",   # מושב אחורי שני
    "last_child_rotated": "יואב" # מעקב אחר התור האחרון לרוטציה הוגנת בין יואב לעלמה
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת התחלה"""
    await show_status(update, context)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מציג את סידור המושבים הנוכחי ברכב"""
    driver = car_state['driver']
    front = car_state['front']
    rear_left = car_state['rear_left']
    rear_right = car_state['rear_right']

    warning_text = ""
    if driver == "דורון":
        warning_text = "\n⚠️ *שים לב:* הילד שיושב מאחורי דורון עלול לסבול מחוסר מקום כי הכסא שלו אחורה."

    text = (
        "🚗 *סידור המושבים המשפחתי מעודכן:*\n\n"
        f"🧑‍✈️ *נהג/ת:* {driver}\n"
        f"💺 *מקדימה:* {front}\n"
        f"⬅️ *מאחורי הנהג (שמאלי):* {rear_left}\n"
        f"➡️ *מושב אחורי נוסף (ימני):* {rear_right}"
        f"{warning_text}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("מי יושב מאחורי אמא?", callback_data="who_behind_mom")],
        [InlineKeyboardButton("חשב סידור מאוזן לילדים (רוטציה)", callback_data="balance_kids")],
        [InlineKeyboardButton("החלף נהג (אפרת ⇄ דורון)", callback_data="toggle_driver")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בלחיצות על הכפתורים"""
    query = update.callback_query
    data = query.data

    if data == "who_behind_mom":
        if car_state["driver"] == "אפרת":
            person = car_state["rear_left"]
            msg = f"מאחוריך (מאחורי כיסא הנהג שלך) יושב/ת: *{person}* 💺"
        else:
            person = car_state["rear_right"]
            msg = f"דורון נוהג ואת מקדימה. הילד שמאחוריך/בצד שלך הוא: *{person}* 💺"
        await query.answer(msg, show_alert=True)

    elif data == "balance_kids":
        # רוטציה הוגנת בין יואב לעלמה
        if car_state["last_child_rotated"] == "יואב":
            car_state["rear_left"] = "עלמה"
            car_state["rear_right"] = "יואב"
            car_state["last_child_rotated"] = "עלמה"
            rotation_msg = "התור התעדכן: עלמה במושב השמאלי, יואב בימני."
        else:
            car_state["rear_left"] = "יואב"
            car_state["rear_right"] = "עלמה"
            car_state["last_child_rotated"] = "יואב"
            rotation_msg = "התור התעדכן: יואב במושב השמאלי, עלמה בימני."
        
        await query.answer(rotation_msg, show_alert=True)
        await show_status(update, context)

    elif data == "toggle_driver":
        if car_state["driver"] == "אפרת":
            car_state["driver"] = "דורון"
            car_state["front"] = "אפרת"
        else:
            car_state["driver"] = "אפרת"
            car_state["front"] = "דורון"
        await show_status(update, context)

def main():
    TOKEN = "9137167147:AAGdLIRC5rANkR3t250DAx_o-QsA1Vv1mlo"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("הבוט החכם לסידור הרכב רץ...")
    app.run_polling()

if __name__ == '__main__':
    main()
 
