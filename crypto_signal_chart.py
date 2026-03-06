#!/usr/bin/env python3
"""Genera una gráfica de señales de compra/venta para una criptomoneda.

Estrategia educativa (no asesoría financiera):
- Tendencia alcista: EMA corta cruza por encima de EMA larga.
- Compra sugerida: cruce alcista + RSI < umbral de sobreventa recuperándose.
- Venta sugerida: cruce bajista o RSI en sobrecompra.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


@dataclass
class Config:
    symbol: str
    period: str
    interval: str
    ema_short: int
    ema_long: int
    rsi_window: int
    rsi_buy: float
    rsi_sell: float


def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def build_signals(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    data = df.copy()
    data["ema_short"] = data["Close"].ewm(span=cfg.ema_short, adjust=False).mean()
    data["ema_long"] = data["Close"].ewm(span=cfg.ema_long, adjust=False).mean()
    data["rsi"] = calculate_rsi(data["Close"], cfg.rsi_window)

    data["trend_up"] = data["ema_short"] > data["ema_long"]
    data["cross_up"] = (data["ema_short"] > data["ema_long"]) & (
        data["ema_short"].shift(1) <= data["ema_long"].shift(1)
    )
    data["cross_down"] = (data["ema_short"] < data["ema_long"]) & (
        data["ema_short"].shift(1) >= data["ema_long"].shift(1)
    )

    data["buy_signal"] = data["cross_up"] & (data["rsi"] < cfg.rsi_buy)
    data["sell_signal"] = data["cross_down"] | (data["rsi"] > cfg.rsi_sell)

    return data


def plot_chart(data: pd.DataFrame, cfg: Config, output: str | None) -> None:
    fig, (ax_price, ax_rsi) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax_price.plot(data.index, data["Close"], label="Precio", linewidth=1.5)
    ax_price.plot(data.index, data["ema_short"], label=f"EMA {cfg.ema_short}", alpha=0.9)
    ax_price.plot(data.index, data["ema_long"], label=f"EMA {cfg.ema_long}", alpha=0.9)

    buys = data[data["buy_signal"]]
    sells = data[data["sell_signal"]]

    ax_price.scatter(
        buys.index,
        buys["Close"],
        marker="^",
        color="green",
        s=90,
        label="Compra sugerida",
        zorder=5,
    )
    ax_price.scatter(
        sells.index,
        sells["Close"],
        marker="v",
        color="red",
        s=90,
        label="Venta sugerida",
        zorder=5,
    )

    ax_price.set_title(
        f"{cfg.symbol} | Señales técnicas (EMA + RSI)\n"
        "No es asesoría financiera; usar con gestión de riesgo"
    )
    ax_price.set_ylabel("Precio")
    ax_price.legend(loc="upper left")
    ax_price.grid(alpha=0.25)

    ax_rsi.plot(data.index, data["rsi"], color="purple", label="RSI")
    ax_rsi.axhline(cfg.rsi_buy, color="green", linestyle="--", alpha=0.7, label="Zona compra")
    ax_rsi.axhline(cfg.rsi_sell, color="red", linestyle="--", alpha=0.7, label="Zona venta")
    ax_rsi.set_ylabel("RSI")
    ax_rsi.set_ylim(0, 100)
    ax_rsi.grid(alpha=0.25)
    ax_rsi.legend(loc="upper left")

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150)
        print(f"Gráfico guardado en: {output}")
    else:
        plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Genera un gráfico para estimar el inicio de subidas y posibles puntos "
            "de compra/venta en criptomonedas."
        )
    )
    parser.add_argument("symbol", help="Ticker en Yahoo Finance. Ej: BTC-USD, ETH-USD")
    parser.add_argument("--period", default="6mo", help="Periodo histórico (default: 6mo)")
    parser.add_argument(
        "--interval", default="1d", help="Intervalo de velas (default: 1d; también 1h, 4h)"
    )
    parser.add_argument("--ema-short", type=int, default=12, help="EMA corta (default: 12)")
    parser.add_argument("--ema-long", type=int, default=26, help="EMA larga (default: 26)")
    parser.add_argument("--rsi-window", type=int, default=14, help="Ventana RSI (default: 14)")
    parser.add_argument("--rsi-buy", type=float, default=40, help="RSI compra (default: 40)")
    parser.add_argument("--rsi-sell", type=float, default=70, help="RSI venta (default: 70)")
    parser.add_argument("--output", help="Ruta para guardar PNG en vez de mostrar en pantalla")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config(
        symbol=args.symbol,
        period=args.period,
        interval=args.interval,
        ema_short=args.ema_short,
        ema_long=args.ema_long,
        rsi_window=args.rsi_window,
        rsi_buy=args.rsi_buy,
        rsi_sell=args.rsi_sell,
    )

    df = yf.download(cfg.symbol, period=cfg.period, interval=cfg.interval, auto_adjust=True)
    if df.empty:
        raise SystemExit(
            "No se encontraron datos. Verifica el ticker (ej: BTC-USD) y la conectividad."
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    data = build_signals(df, cfg)

    latest = data.dropna().iloc[-1]
    trend_text = "ALCISTA" if latest["trend_up"] else "BAJISTA/LATERAL"
    print(f"Tendencia actual estimada: {trend_text}")

    last_buy = data[data["buy_signal"]].tail(1)
    last_sell = data[data["sell_signal"]].tail(1)

    if not last_buy.empty:
        print(
            f"Última compra sugerida: {last_buy.index[0].date()} "
            f"a ~{last_buy['Close'].iloc[0]:.2f}"
        )
    else:
        print("No hay señal reciente de compra con los parámetros actuales.")

    if not last_sell.empty:
        print(
            f"Última venta sugerida: {last_sell.index[0].date()} "
            f"a ~{last_sell['Close'].iloc[0]:.2f}"
        )
    else:
        print("No hay señal reciente de venta con los parámetros actuales.")

    plot_chart(data, cfg, args.output)


if __name__ == "__main__":
    main()
