# [H] H-01 | Last User Of Epoch Cannot Withdraw Collateral

## Summary
Severity: High
Contest weight: 0.2620
Dataset id: 1979
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LiquidityModule._closeLiquidityPosition, collected amounts are rounded up by adding 1 wei to offset Uniswap’s rounding when opening a position. However, borrowed amounts may be zero (e.g., when adding liquidity outside the current price tick), and collected amounts can also be zero, depending on the price tick. By adding 1 wei, users may withdraw more collateral than they initially deposited. Over time, this leads to the last user in an epoch being unable to withdraw due to insufficient collateral. This behavior can also be exploited by malicious users with the following steps: • Provide liquidity above the current price tick, so only vGas is borrowed and no vETH. • Immediately decrease liquidity, collecting all borrowed vGas plus 1 wei vETH. • The 1 wei of vETH is added to the user's deposited collateral and then withdrawn.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/blob/addf2fcff18ec9adfdc6960d7426f0a1e4595dfd/packages/protocol/test/fuzzing/FoundryPlayground.sol#L594-L609

## Recommendation
1. If collected amount is zero, do not add the 1 wei adjustment. 2. Modify settlePosition to allow payouts of the contract's remaining balance when the exact collateral amount is insufficient, preventing the last withdrawal from reverting if the balance is short by a few wei.
