# [H] H-01 | DoS Via External Liquidity By Predicting Positions

## Summary
Severity: High
Contest weight: 0.2365
Dataset id: 21478
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users adding external liquidity to the protocol's positions should not affect the market making operations, as the liquidity for each range is tracked by the getLiquidity mapping in the BPOOL contract storage.
The issue relies on the way this mapping is updated after an operation completes. When using addReservesTo or addLiquidityTo this mapping will be updated with the new real position liquidity, including externally added liquidity.
An attacker can DoS the sweep operation by following these steps:
1. Add ext liquidity to the projected ANCHOR range after a bump (lowerTick + 1 TS, upperTick).
2. Execute bump(), now the ANCHOR range is the same as the projected one, which we just maliciously added liquidity to.
3. Now the addLiquidityTo function call for the ANCHOR range records the malicious liquidity as belonging to the system.
4. sweep now reverts with underflow.

## Proof of Concept
https://github.com/GuardianAudits/baseline-team-1-pocs/pull/18

## Recommendation
Remove any liquidity that is sitting in positions that will be used, but aren’t currently, and add this amount to the bufferedReserves value.
