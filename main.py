#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRUE CRYPTO ALPHA - AI Trading Bot
Version: 1.0.0
Author: GreatGa
"""

import asyncio
import logging
from datetime import datetime
import ccxt
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrueCryptoAlpha:
    def __init__(self):
        self.version = "1.0.0"
        self.exchange = None
        
    def print_banner(self):
        banner = f"""
{Fore.CYAN}{'='*60}
{Fore.YELLOW}  🚀 TRUE CRYPTO ALPHA v{self.version}
{Fore.GREEN}  💡 Самообучающийся AI торговый бот
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
        """
        print(banner)
        
    async def setup_exchange(self):
        """Initialize Binance connection"""
        try:
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
            })
            logger.info(f"{Fore.GREEN}✅ Binance API подключено!{Style.RESET_ALL}")
            return True
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Ошибка подключения: {e}{Style.RESET_ALL}")
            return False
    
    async def get_market_data(self, symbol='BTC/USDT'):
        """Get current market price"""
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    async def run(self):
        """Main bot loop"""
        self.print_banner()
        
        # Setup exchange
        if not await self.setup_exchange():
            return
        
        logger.info(f"{Fore.CYAN}📊 Начинаю мониторинг рынка...{Style.RESET_ALL}")
        
        pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        while True:
            try:
                for pair in pairs:
                    ticker = await self.get_market_data(pair)
                    if ticker:
                        price = ticker['last']
                        change = ticker['percentage']
                        
                        color = Fore.GREEN if change > 0 else Fore.RED
                        logger.info(
                            f"{Fore.YELLOW}{pair}{Style.RESET_ALL}: "
                            f"${price:,.2f} {color}({change:+.2f}%){Style.RESET_ALL}"
                        )
                
                await asyncio.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info(f"{Fore.YELLOW}⚠️ Получен сигнал остановки...{Style.RESET_ALL}")
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
