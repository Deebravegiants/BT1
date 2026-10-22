# [M] Vault.withdraw_underlying_to_claim can be called by anyone with any _min_weth_out param

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404
Type: audit-issue

## Details
# Vault.withdraw_underlying_to_claim can be called by anyone with any _min_weth_out param

## Summary
Vault.withdraw_underlying_to_claim can be called by anyone with any _min_weth_out param. Because of that user attacker can call this function with smallest slippage and make loses to funders.
## Vulnerability Detail
Vault.withdraw_underlying_to_claim can be called by anyone. User also provides `_min_weth_out` param which is needed as slippage. 
Later this is used in order to withdraw underlying form alchemix contract. 

Attacker can use this in order to make loses for funders. He can call this function with small slippage and make contract withdraw small amount of weth. 
## Impact
Lose of funds for funders.
## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404
## Tool used

Manual Review

## Recommendation
You need to compute slippage yourself, according to `_amount_shares` param.
