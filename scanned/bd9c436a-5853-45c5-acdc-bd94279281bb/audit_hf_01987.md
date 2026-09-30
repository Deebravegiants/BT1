# [H] Liquidations can be prevented by updating the SL timeout before it expires

## Summary
Severity: High
Contest weight: 0.0991
Dataset id: 11149
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Traders who continually update their stop losses before the SL timeout expires will never face liquidation. This is because liquidating via a LimitOrder of type LIQ is impossible when the limit order includes a stop loss. Additionally, triggering the stop loss with a LimitOrder of type SL is hindered by the timeout check.

## Recommendation
If the trade is liquidatable, disregard the timeout for stop losses.
