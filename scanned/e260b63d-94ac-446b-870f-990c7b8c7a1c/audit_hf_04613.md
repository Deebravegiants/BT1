# [M] M-12 | Same Heartbeat For Multiple Oracles

## Summary
Severity: Medium
Contest weight: 0.0599
Dataset id: 22218
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getPriceUSD18 makes requests to a base and quote asset oracles. If any of them has been updated more than maxOracleDelay seconds ago, _isBadData will be set to true. Since not all feeds have the same heartbeat, if the oracle uses two feeds with different ones, it may happen that one of the prices is stale, but it's accepted as a valid one.

## Recommendation
Use two different delay variables - one for the base feed and one for the quote feed.
