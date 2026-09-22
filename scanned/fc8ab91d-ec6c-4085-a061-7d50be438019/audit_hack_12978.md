# [M] Precision loss in successive divisions

## Summary
Severity: Medium
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1069-L1076
Type: audit-issue

## Details
# Precision loss in successive divisions

## Summary
Precision loss in successive divisions
## Vulnerability Detail
The function `_debt_interest_since_last_update()` calculates the debt interest accrued since the last debt update.The issue of precision loss arises when performing successive divisions, especially when working with floating-point numbers or decimals. This loss of precision occurs due to the finite precision of numerical representations used in computers.

In the given code snippet, there are two division operations. First, the expression (block.timestamp - self.last_debt_update[_debt_token]) is calculated, and then it is multiplied by self._current_interest_per_second(_debt_token). Next, the result is multiplied by self.total_debt_amount[_debt_token] and divided by PERCENTAGE_BASE and PRECISION.

During each division operation, the result may be rounded or truncated to fit the available number of decimal places or significant figures. This can lead to a loss of precision, as the decimal values are approximated or truncated, potentially resulting in inaccurate calculations.
```solidity
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```

## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1069-L1076
## Tool used

Manual Review

## Recommendation
To mitigate this issue, alternative approaches such as using fixed-point arithmetic or higher precision data types can be employed to preserve the precision and accuracy of calculations.
