# [H] Current method for distributing rewards has serious accounting errors

## Summary
Severity: High
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404
Type: audit-issue

## Details
# Current method for distributing rewards has serious accounting errors

## Summary

When deposits are made the number of shares yield are stored directly. When underlying is claimed it reduces the amount of underlying in the contract (as well as shares owned by the contract) but the amount of shares owned by depositors is still the same. This leads to serious issues when users liquidate and will result in vault insolvency.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404

Shares are withdrawn from Alchemix and the resulting WETH is distributed to depositors via increase to amount_claimable_per_share. This action reduces the number of shares owned by the contract but the depositors are still owed the same amount of shares. The result is a token accounting error and result in insolvency.

Example:
Assume for simplicity that 1 WETH = 1 YVETH (i.e. 1 WETH = 1 share). User A deposits 1 WETH resulting in 1 share and 0.5 alETH being minted to the recipient. Over time the loan is paid back automatically and the total debt of the contract drops to 0.4. Now that the debt has dropped withdraw_underlying_to_claim can be called, reducing the amount of underlying WETH to 0.8 and paying out 0.2 WETH to User A. User A then decides to liquidate his token. This results in a collateralization of 2 (0.8/0.4). Since the number of shares owed User A is 1, the contract attempts to liquidate 0.5 shares. Due to constraints within AlchemistV2 only 0.4 shares are actually liquidated. This results in the vault attempting to withdraw 0.6 shares. This call will revert because the vault only actually has 0.4 shares. The result is that liquidation is broken. 

## Impact

Accounting errors in share counts result in liquidation being broken

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352

## Tool used

Manual Review

## Recommendation

Create a secondary share that tracks the exchange rate between alchemix shares and vault shares
