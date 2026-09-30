# [C] Wrong price calculation from Gold to USDC

## Summary
Severity: Critical
Contest weight: 0.7406
Dataset id: 5766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the mint_gold(), burn_gold(), buy() and sell() functions, the USDC amount required or received is calculated based on these formulas:
```solidity
// in buy() and mint_gold()
amount * price / 100 * (10000 + self.price.fee)
// in sell() and buy_gold()
amount * price / 100 * (10000 - self.price.fee)
```
These formulas are incorrect due to several issues:
1. They don't account for the Pyth price feed exponential value of XAU/USD.
2. They fail to handle the decimal differences between Gold token and USDC token properly.
3. They don't divide by price.fee's denominator (10000) after multiplication.
4. They divide first and then multiply, which leads to precision loss.

## Recommendation
The formulas should be corrected as follows (in pseudocode):
```solidity
// in buy() and mint_gold()
- amount * price / 100 * (10000 + self.price.fee)
+ amount * price * (10000 + self.price.fee) * pow(10, mint_b.decimals - mint_a.decimals) * pow(10, pyth_price_result?.exponent) / 10000
// in sell() and buy_gold()
- amount * price / 100 * (10000 - self.price.fee)
+ amount * price * (10000 - self.price.fee) * pow(10,mint_b.decimals - mint_a.decimals) * pow(10, pyth_price_result?.exponent) / 10000
```
