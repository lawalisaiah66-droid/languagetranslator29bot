import os
import logging
import asyncio
from typing import Optional, Dict, Any
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    ContextTypes,
    filters
)
from googletrans import Translator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Complete language dictionary (100+ languages)
LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
    'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
    'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese Simplified',
    'zh-tw': 'Chinese Traditional', 'co': 'Corsican', 'hr': 'Croatian',
    'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
    'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian',
    'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
    'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew', 'hi': 'Hindi',
    'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo',
    'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
    'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer',
    'rw': 'Kinyarwanda', 'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz',
    'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian',
    'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
    'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi',
    'mn': 'Mongolian', 'my': 'Myanmar', 'ne': 'Nepali', 'no': 'Norwegian',
    'or': 'Odia', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish',
    'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
    'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho',
    'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese',
    'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil',
    'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish',
    'tk': 'Turkmen', 'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur',
    'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa',
    'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

# Default target language
DEFAULT_TARGET = 'en'

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    welcome_msg = (
        f"🌍 **Hello {user.first_name}!**\n\n"
        f"I'm a powerful Language Translator Bot!\n\n"
        f"📌 **How to use me:**\n"
        f"• Send any text → Auto-translates to English\n"
        f"• /translate [lang] [text] → Translate to specific language\n"
        f"• /languages → See all 100+ supported languages\n"
        f"• @languagetranslator29bot → Use inline in any chat\n\n"
        f"💡 **Examples:**\n"
        f"• Send: `Bonjour le monde`\n"
        f"• /translate es Hello world\n"
        f"• @languagetranslator29bot Hola mundo\n\n"
        f"🔧 **Commands:** /help for more options"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_msg = (
        "📚 **Available Commands:**\n\n"
        "/start - Welcome message\n"
        "/help - Show this help menu\n"
        "/languages - List all supported languages\n"
        "/translate [lang] [text] - Translate to specific language\n"
        "/about - About this bot\n\n"
        "🌐 **Quick Usage:**\n"
        "• Send text → Auto-translate to English\n"
        "• @languagetranslator29bot text → Inline translation\n\n"
        "📝 **Language Codes Examples:**\n"
        "• es → Spanish\n"
        "• fr → French\n"
        "• de → German\n"
        "• ja → Japanese\n"
        "• zh-cn → Chinese Simplified\n\n"
        "🔍 Type /languages for the complete list"
    )
    await update.message.reply_text(help_msg, parse_mode='Markdown')


async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /languages command."""
    # Format language list
    lang_list = [f"• `{code}` → {name}" for code, name in sorted(LANGUAGES.items())]
    
    # Split into chunks of 30 languages per message
    chunk_size = 30
    chunks = [lang_list[i:i+chunk_size] for i in range(0, len(lang_list), chunk_size)]
    
    # Send first chunk with header
    await update.message.reply_text(
        f"🌐 **Supported Languages ({len(LANGUAGES)}):**\n\n" + "\n".join(chunks[0]),
        parse_mode='Markdown'
    )
    
    # Send remaining chunks
    for chunk in chunks[1:]:
        await update.message.reply_text(
            "\n".join(chunk),
            parse_mode='Markdown'
        )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    about_msg = (
        "🤖 **Language Translator Bot**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ **Features:**\n"
        "• 100+ languages supported\n"
        "• Auto language detection\n"
        "• Inline mode support\n"
        "• Fast & reliable translation\n"
        "• Free to use\n\n"
        "🛠️ **Technology:**\n"
        "• Python 3.11+\n"
        "• python-telegram-bot\n"
        "• Google Translate API\n"
        "• Deployed on Railway\n\n"
        "📦 **Version:** 2.0.0\n"
        "👨‍💻 **Developer:** @YourUsername\n"
        "🐙 **Source:** [GitHub](https://github.com/yourusername/telegram-translator-bot)"
    )
    await update.message.reply_text(about_msg, parse_mode='Markdown', disable_web_page_preview=True)


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command."""
    try:
        # Check if arguments are provided
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ **Usage:** `/translate [language_code] [text]`\n\n"
                "Example: `/translate es Hello world`\n"
                "Type /languages to see all supported codes.",
                parse_mode='Markdown'
            )
            return
        
        # Extract target language and text
        target_lang = context.args[0].lower()
        text = " ".join(context.args[1:])
        
        # Validate language code
        if target_lang not in LANGUAGES:
            await update.message.reply_text(
                f"❌ Invalid language code: `{target_lang}`\n"
                f"Type /languages to see all supported codes.",
                parse_mode='Markdown'
            )
            return
        
        # Perform translation
        await perform_translation(update.message, text, target_lang)
        
    except Exception as e:
        logger.error(f"Translate command error: {e}")
        await update.message.reply_text(
            "❌ An error occurred. Please try again later."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    text = update.message.text
    await perform_translation(update.message, text, DEFAULT_TARGET)


async def perform_translation(message, text: str, target_lang: str) -> None:
    """Core translation function."""
    try:
        # Show typing indicator
        await message.chat.send_action(action="typing")
        
        # Detect source language
        detection = translator.detect(text)
        source_lang = detection.lang
        source_lang_name = LANGUAGES.get(source_lang, source_lang.upper())
        target_lang_name = LANGUAGES.get(target_lang, target_lang.upper())
        
        # Perform translation
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text
        
        # Prepare response
        response = (
            f"🔍 **Detected:** {source_lang_name}\n"
            f"🎯 **Target:** {target_lang_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Translation:**\n"
            f"{translated_text}"
        )
        
        # Truncate if too long (Telegram limit: 4096 characters)
        if len(response) > 4096:
            response = response[:4000] + "...\n\n⚠️ Text was truncated."
        
        await message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await message.reply_text(
            "❌ Sorry, I couldn't translate that text. Please try again with shorter text."
        )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries."""
    query = update.inline_query.query.strip()
    
    # Show help if no query
    if not query:
        results = [
            InlineQueryResultArticle(
                id='help',
                title='🌍 Translate to English',
                description='Send text to translate',
                input_message_content=InputTextMessageContent(
                    "📝 **How to use inline mode:**\n\n"
                    "Type: @languagetranslator29bot [text]\n"
                    "Example: @languagetranslator29bot Bonjour\n\n"
                    "Or specify language:\n"
                    "@languagetranslator29bot es Hello"
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=60)
        return
    
    # Parse query: @bot [lang] text
    parts = query.split(maxsplit=1)
    target_lang = DEFAULT_TARGET
    text = query
    
    # Check if first part is a language code
    if len(parts) == 2 and parts[0].lower() in LANGUAGES:
        target_lang = parts[0].lower()
        text = parts[1]
    
    try:
        # Detect source language
        detection = translator.detect(text)
        source_lang = detection.lang
        source_lang_name = LANGUAGES.get(source_lang, source_lang.upper())
        target_lang_name = LANGUAGES.get(target_lang, target_lang.upper())
        
        # Translate
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text
        
        # Create result
        result_text = (
            f"🔍 {source_lang_name} → {target_lang_name}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{translated_text}"
        )
        
        results = [
            InlineQueryResultArticle(
                id='translation',
                title=f'🌐 {target_lang_name} translation',
                description=translated_text[:100] + ('...' if len(translated_text) > 100 else ''),
                input_message_content=InputTextMessageContent(
                    result_text,
                    parse_mode='Markdown'
                )
            )
        ]
        
        await update.inline_query.answer(results, cache_time=300)
        
    except Exception as e:
        logger.error(f"Inline translation error: {e}")
        results = [
            InlineQueryResultArticle(
                id='error',
                title='⚠️ Translation failed',
                description='Please try again',
                input_message_content=InputTextMessageContent(
                    "❌ Translation failed. Please try again."
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=60)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass


async def post_init(application: Application) -> None:
    """Called after bot initialization."""
    logger.info("Bot started successfully! 🤖")
    logger.info(f"Bot Username: @languagetranslator29bot")
    logger.info(f"Supported Languages: {len(LANGUAGES)}")


def main() -> None:
    """Main entry point."""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("translate", translate_command))
        
        # Add message handler for text messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        ))
        
        # Add inline query handler
        application.add_handler(InlineQueryHandler(inline_query))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
