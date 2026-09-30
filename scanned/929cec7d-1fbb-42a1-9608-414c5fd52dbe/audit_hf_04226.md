# [M] M-20 | Risk Free Trade With Account Permissions

## Summary
Severity: Medium
Contest weight: 0.1266
Dataset id: 21120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PoC Similarly to M-09, it is possible to make a short term risk free trade by preventing keepers from executing an account’s order by including a splitAccount callback where no keeper is granted the necessary _PERPS_MODIFY_COLLATERAL_PERMISSION for the fromId account. As a result, a malicious user may prevent an order from being executable in the block where the valid price data is accurate and only allow the order to go through once a significant period of time has passed and the user observes that the true current price of the index asset has moved in their favor. The order will only be executable with the outdated price, and therefore the user will realize a risk-free profit based upon how much price has diverged in the user’s favor since then.

## Recommendation
Consider increasing the orderFee percentage that is taken to dissuade from any risk-free short term trades. Otherwise consider removing the possibility for users to control whether or not their orders are executable by way of callbacks through a try/catch wrapper around the callbacks.
