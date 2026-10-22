# [M] 5.1 ZkBobPool Withdrawal Sandwich Attack

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

When the withdrawal with native_amount is submitted to the ZkBobPool, the sale of tokens for ETH
happens using the UniswapV3Seller contract. However, the amountOutMinimum parameter of this
swap is 0. A potential attacker can place orders that would manipulate the price, forcing the sellForETH
trade to be executed with a bad price. Thus, due to the lack of spread control, any use of
UniswapV3Seller can result in a bad trade, allowing price manipulators to pocket the profit from this
trade.

Risk accepted:

BOB Protocol responded:

```
This feature is only intended to swap small amounts of tokens, purely for funding wallets with gas
tokens. UI will strongly dissuade users for doing swaps that are larger than e.g. 100$ in value. Added
a warning comment to the sellForETH function.
```
