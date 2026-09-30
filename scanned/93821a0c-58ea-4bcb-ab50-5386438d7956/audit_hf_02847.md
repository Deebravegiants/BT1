# [H] Misuse of SOL/USDC Price Feed for USDT Calculations

## Summary
Severity: High
Contest weight: 0.1863
Dataset id: 15854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The code uses the SOL_USDC_FEED to fetch the price of SOL in USDC:
```sol
const SOL_USDC_FEED: &str =
"J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix";
```
And uses this price to perform calculations in USDT:
```sol
let current_price = price_feed.get_price_no_older_than(current_timestamp,
STALENESS_THRESHOLD);
```
While USDC and USDT are both stablecoins, they are distinct assets and do not always maintain a 1:1 value, especially during market volatility. A historical example is the USDC depeg in 2023 when it dropped to 0.80 USD. If such a depeg occurs again, it could be exploited by malicious users to purchase ICO tokens at a significantly reduced rate, leading to financial losses for the project.

## Recommendation
Replace the SOL/USDC feed with a direct SOL/USDT price feed to ensure accurate and relevant price calculations.
