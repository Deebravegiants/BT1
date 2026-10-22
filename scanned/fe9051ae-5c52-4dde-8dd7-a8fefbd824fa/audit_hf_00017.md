# [H] PORT-4 | Supported Token Removal Gamed

## Summary
Severity: High
Contest weight: 0.1746
Dataset id: 93
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a token is removed from the assetsArray with the removeAsset function, it can no longer be used as margin when a portfolio is liquidated. When the owner calls the removeAsset function, a malicious actor can front-run the transaction and make a large trade using the soon-to-be-removed token as margin. After the admin's transaction goes through, the attacker can freely withdraw the now unsupported token through the withdrawAssets function. When the portfolio is attempted to be liquidated, the liquidation will fail as the PnL is assigned to the dollar value of the portfolio, which is 0, and the totalFee is attempted to be subtracted from the PnL.

## Recommendation
Only remove supported tokens when options are not tradeable or the protocol is paused.
