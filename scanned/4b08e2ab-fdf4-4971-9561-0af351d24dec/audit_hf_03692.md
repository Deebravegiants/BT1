# [M] Deposit and withdraw to the vault with the

## Summary
Severity: Medium
Contest weight: 0.1764
Dataset id: 19788
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function vault.deposit and vault.withdraw of vault in contract PerpDepository need to be passed with the amount in raw decimal of tokens (is different from 18 in case using USDC, WBTC, ... as base and quote tokens). But some calls miss the conversion of decimals from 18 to token's decimal, and pass wrong decimals to them.
• Function vault.deposit need to be passed the param amount in token's decimal (as same as vault.withdraw). You can see at function _depositAsset in contract PerpDepository.
• But there are some calls of vault.deposit and vault.withdraw that passed the amount in the wrong decimal (18 decimal). Let's see function _rebalanceNegativePnlWithSwap in contract PerpDepository:
Because function _placePerpOrder returns in decimal 18 (confirmed with sponsor with the above call. It leads to vault using the wrong decimal when depositing and withdrawing tokens.
• There is another case that use vault.withdraw with the wrong decimal (same as this case) in function _rebalanceNegativePnlLite:
Because of calling vault.deposit and vault.withdraw with the wrong decimal of the param amount, the protocol can lose a lot of funds. And some functionalities of the protocol can be broken cause it can revert by not enough allowance when calling these functions.

## Recommendation
Should convert the param amount from token's decimal to decimal 18 before vault.deposit and vault.withdraw.
