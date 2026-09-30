# [M] _account_for_withdraw_liquidity rounding in

## Summary
Severity: Medium
Contest weight: 0.2068
Dataset id: 20170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vault implementers should be aware of the need for specific, opposing rounding directions across the different mutable and view methods, as it is considered most secure to favor the Vault itself during calculations over its users. If (1) it’s calculating how many shares to issue to a user for a certain amount of the underlying tokens they provide or (2) it’s determining the amount of the underlying tokens to transfer to them for returning a certain amount of shares, it should round down. If (1) it’s calculating the amount of shares a user has to supply to receive a given amount of the underlying tokens or (2) it’s calculating the amount of underlying tokens a user has to provide to receive a certain amount of shares, it should round up.
When the user extracts liquidity, due to the existence of share, the calculation has precision errors, should pay special attention to the rounding direction. Users withdraw a specific amount of liquidity, user shares should be rounded up, subtract 1 more shares, to avoid spending more than they earn, resulting in the eventual run out of the vault.
_amount_to_lp_shares calculates the amount of share to be subtracted, which should round up, otherwise the user account share will be 1 more than it actually is, and the difference will gradually become larger as users interact with vault over time, eventually run out of the vault.
Rounding in the wrong direction, when users withdraw liquidity, the shares are greater than actual value, and gradually accumulate as interactions, eventually causing the vault to be run out of and unable to repay all the liquidity.

## Recommendation
Round up in _amount_to_lp_shares
