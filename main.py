#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRUE CRYPTO ALPHA v2.0 - Full Version
Технический анализ + Генерация сигналов + Telegram
"""

import asyncio
import logging
from datetime import datetime
import os
import ccxt
import pandas as pd
import numpy as np
from colorama import Fore, Style, init

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram settings (optional)
TELEGRAM_ENABLED = os.getenv('TELEGRAM_BOT_TOKEN') is not None

if TELEGRAM_ENABLED:
    try:
        from telegram import Bot
        telegram_bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        logger.info(f"{Fore.GREEN}✅ Telegram подключен!{Style.RESET_ALL}")
    except:
        TELEGRAM_ENABLED = False
        logger.warning(f"{Fore.YELLOW}⚠️ Telegram не настроен{Style.RESET_ALL}")

class TechnicalAnalysis:
    """Технический анализ"""
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """RSI индикатор"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    @staticmethod
    def calculate_ema(data, period):
        """EMA индикатор"""
        ema = data.ewm(span=period, adjust=False).mean()
        return ema.iloc[-1]
    
    @staticmethod
    def calculate_macd(data):
        """MACD индикатор"""
        ema12 = data.ewm(span=12, adjust=False).mean()
        ema26 = data.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1] - signal.iloc[-1]
    
    @staticmethod
    def analyze(df):
        """Полный анализ"""
        close = df['close']
        
        rsi = TechnicalAnalysis.calculate_rsi(close)
        ema20 = TechnicalAnalysis.calculate_ema(close, 20)
        ema50 = TechnicalAnalysis.calculate_ema(close, 50)
        macd = TechnicalAnalysis.calculate_macd(close)
        
        current_price = close.iloc[-1]
        
        return {
            'rsi': rsi,
            'ema20': ema20,
            'ema50': ema50,
            'macd': macd,
            'current_price': current_price
        }

class SignalGenerator:
    """Генератор торговых сигналов"""
    
    @staticmethod
    def generate(analysis, pair):
        """Генерация сигнала"""
        rsi = analysis['rsi']
        price = analysis['current_price']
        ema20 = analysis['ema20']
        ema50 = analysis['ema50']
        macd = analysis['macd']
        
        signal = None
        confidence = 0
        
        # LONG сигнал
        if rsi < 35 and price > ema20 and macd > 0:
            signal = 'LONG'
            confidence = min(95, 60 + (35 - rsi) + (10 if price > ema50 else 0))
            take_profit = price * 1.025
            stop_loss = price * 0.985
        
        # SHORT сигнал  
        elif rsi > 65 and price < ema20 and macd < 0:
            signal = 'SHORT'
            confidence = min(95, 60 + (rsi - 65) + (10 if price < ema50 else 0))
            take_profit = price * 0.975
            stop_loss = price * 1.015
        
        if signal and confidence >= 70:
            return {
                'type': signal,
                'pair': pair,
                'price': price,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'confidence': confidence,
                'rsi': rsi,
                'macd': 'Позитивный' if macd > 0 else 'Негативный'
            }
        
        return None

class TrueCryptoAlpha:
    def __init__(self):
        self.version = "2.0.0"
        self.exchange = None
        self.pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
        
    def print_banner(self):
        banner = f"""
{Fore.CYAN}{'='*70}
{Fore.YELLOW}  🚀 TRUE CRYPTO ALPHA v{self.version} - FULL VERSION
{Fore.GREEN}  💡 Технический анализ + Генерация сигналов + Telegram
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
        """
        print(banner)
        
    async def setup_exchange(self):
        try:
            self.exchange = ccxt.binance({'enableRateLimit': True})
            logger.info(f"{Fore.GREEN}✅ Binance API подключено!{Style.RESET_ALL}")
            return True
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return False
    
    async def get_ohlcv(self, symbol, timeframe='15m', limit=100):
        """Получить свечи"""
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv, symbol, timeframe, limit=limit
            )
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return None
    
    async def send_telegram_signal(self, signal):
        """Отправить сигнал в Telegram"""
        if not TELEGRAM_ENABLED:
            return
        
        try:
            emoji = "📈" if signal['type'] == 'LONG' else "📉"
            
            message = f"""
🚀 <b>TRUE CRYPTO ALPHA - Сигнал!</b>

📢 <b>Открытие: {signal['type']} {emoji}</b>
💱 <b>Pair:</b> {signal['pair']}
📊 <b>Цена:</b> ${signal['price']:,.2f}
🎯 <b>Тейк профит:</b> ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)
🛡️ <b>Стоп лосс:</b> ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)
🎯 <b>Confidence:</b> {signal['confidence']:.0f}%

🧠 <b>AI Анализ:</b>
• RSI: {signal['rsi']:.1f}
• MACD: {signal['macd']}
• Тренд: {'Bullish' if signal['type']=='LONG' else 'Bearish'}

⚠️ <i>Риск - твоя ответственность!</i>
            """
            
            await asyncio.to_thread(
                telegram_bot.send_message,
                chat_id=telegram_chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"{Fore.GREEN}📱 Сигнал отправлен в Telegram!{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Telegram error: {e}")
    
    async def analyze_and_signal(self, pair):
        """Анализ и генерация сигнала"""
        df = await self.get_ohlcv(pair)
        if df is None or len(df) < 50:
            return None
        
        analysis = TechnicalAnalysis.analyze(df)
        signal = SignalGenerator.generate(analysis, pair)
        
        return signal
    
    async def run(self):
        self.print_banner()
        
        if not await self.setup_exchange():
            return
        
        logger.info(f"{Fore.CYAN}📊 Начинаю мониторинг {len(self.pairs)} пар...{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}⏰ Анализ каждые 2 минуты{Style.RESET_ALL}")
        
        if TELEGRAM_ENABLED:
            logger.info(f"{Fore.GREEN}📱 Telegram сигналы активны!{Style.RESET_ALL}")
        else:
            logger.info(f"{Fore.YELLOW}📱 Telegram не настроен (работаем без него){Style.RESET_ALL}")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                logger.info(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
                logger.info(f"{Fore.YELLOW}🔍 Анализ #{iteration} - {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
                logger.info(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
                
                for pair in self.pairs:
                    logger.info(f"\n{Fore.CYAN}Анализирую {pair}...{Style.RESET_ALL}")
                    
                    signal = await self.analyze_and_signal(pair)
                    
                    if signal:
                        logger.info(f"{Fore.GREEN}🎯 СИГНАЛ НАЙДЕН!{Style.RESET_ALL}")
                        logger.info(f"{Fore.YELLOW}  Тип: {signal['type']}{Style.RESET_ALL}")
                        logger.info(f"  Цена: ${signal['price']:,.2f}")
                        logger.info(f"  Confidence: {signal['confidence']:.0f}%")
                        
                        await self.send_telegram_signal(signal)
                    else:
                        logger.info(f"{Fore.YELLOW}  Нет сильных сигналов{Style.RESET_ALL}")
                    
                    await asyncio.sleep(2)
                
                logger.info(f"\n{Fore.GREEN}✅ Анализ завершён. Ожидание 2 минуты...{Style.RESET_ALL}")
                await asyncio.sleep(120)
                
            except KeyboardInterrupt:
                logger.info(f"{Fore.YELLOW}\n⚠️ Остановка бота...{Style.RESET_ALL}")
                break
            except Exception as e:
                logger.error(f"{Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    bot = TrueCryptoAlpha()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Бот остановлен. До встречи!{Style.RESET_ALL}")
