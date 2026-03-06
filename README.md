# AI Brain Project

## Gráfico de señales para crypto (compra/venta)

Se agregó `crypto_signal_chart.py`, un script en Python que:

- Descarga datos históricos desde Yahoo Finance.
- Calcula tendencia con cruce de EMAs (12/26 por defecto).
- Calcula RSI para detectar zonas de compra/venta.
- Marca en el gráfico señales sugeridas de compra (▲) y venta (▼).

> ⚠️ Es una herramienta educativa. No garantiza resultados ni reemplaza gestión de riesgo.

### Requisitos

```bash
pip install yfinance pandas matplotlib
```

### Uso rápido

```bash
python crypto_signal_chart.py BTC-USD --period 6mo --interval 1d --output btc_signals.png
```

Parámetros útiles:

- `--ema-short 12 --ema-long 26`
- `--rsi-buy 40 --rsi-sell 70`
- `--period` (`1mo`, `3mo`, `6mo`, `1y`, etc.)
- `--interval` (`1h`, `4h`, `1d`)

Ejemplo para ETH:

```bash
python crypto_signal_chart.py ETH-USD --period 1y --interval 1d --output eth_signals.png
```
