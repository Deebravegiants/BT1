# [M] load_price_feed_from_account_info is deprecated

## Summary
Severity: Medium
Contest weight: 0.0707
Dataset id: 15857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function load_price_feed_from_account_info in the Pyth SDK for Solana has been deprecated.
```sol
use pyth_sdk_solana::{load_price_feed_from_account_info, PriceFeed};
```
The function has been deprecated since version 0.10.x of pyth_sdk_solana. In dependencies, we see that the protocol currently uses: pyth-sdk-solana = "0.10.1". This means that this function is no longer recommended for use. Reference - Link

## Recommendation
The recommended alternative is to use SolanaPriceAccount::account_info_to_feed instead.
