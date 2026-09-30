# [M] GLOBAL-1 | Risk-Fee Trade During Equity Events

## Summary
Severity: Medium
Contest weight: 0.1111
Dataset id: 20552
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pyth provides price feeds for numerous US equities with significant dividends. A position on a share that pays a dividend will see its price adjusted to reflect the dividend payment. For example, with a dividend of $1 per share, a stock that was trading at $100 will drop to $99 on the ex-dividend date. Furthermore, stocks may go through splits and reverse stock splits, drastically changing the price of a share.
Consider the following scenario:
A trader anticipates a stock split so they sell 1 share for $100
A 2:1 stock split occurs and the new price is $50
The trader closes their short, making a risk-free profit.

## Recommendation
Exercise caution with which markets are supported for trading and carefully monitor for equity events as they are announced in advanced. In anticipation of an event, put the market in close-only mode and pause the market afterwards to prevent further trading. Ensure the market starts from a clean slate post-event.
