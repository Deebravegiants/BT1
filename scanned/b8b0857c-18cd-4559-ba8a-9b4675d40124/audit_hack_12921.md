# [M] Vault.vy: Immediate Liquidation Risk due to Maximum Leverage Utilization and Slippage

## Summary
Severity: Medium
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L175
Type: audit-issue

## Details
# Vault.vy: Immediate Liquidation Risk due to Maximum Leverage Utilization and Slippage

## Summary
A vulnerability has been identified in the `Vault.sol` smart contract, wherein traders using maximum leverage during position opening may become immediately eligible for liquidation due to market slippage.

## Vulnerability Detail
In the process of opening a position, the contract allows the setting of leverage up to `max_leverage` via `assert ((_debt_amount + _margin_amount) * PRECISION / _margin_amount) <= self.max_leverage[_debt_token][_position_token] * PRECISION, "too much leverage"`. 
However, the function `_is_liquidatable` considers a position eligible for liquidation if the leverage exceeds `max_leverage`. Due to the inherent slippage during position opening, a position that's been opened at `max_leverage` could immediately become eligible for liquidation.

Currently, the beta site allows the use of up to 50x leverage. For certain users, this is a viable level of leverage, which, could result in immediate liquidation and significant losses.

## Impact
The impact of this vulnerability is that it could cause immediate liquidation for traders using high leverage, especially those using the maximum permissible leverage. This could result in significant financial losses for these traders, affecting their confidence in the platform.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L175

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L485-L495

## Tool used

Manual Review

## Recommendation
It's recommended to differentiate the `max_leverage` for position opening and the leverage level used for the liquidation condition, ideally by introducing a safety margin. This safety margin would provide a buffer to prevent immediate liquidation due to market slippage.
