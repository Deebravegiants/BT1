# [M] Donating (and syncing) tokens to an Aero-

## Summary
Severity: Medium
Contest weight: 0.1293
Dataset id: 22683
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can bypass the exposure limits by donating tokens to an Aerodrome pool in which he owns ~100% of the liquidity, this will inflate reserves which will increase the value of the collateral and the attacker won't lose capital because he owns ~100% of the liquidity.
Attack scenario:
1. Create a new Aerodrome pool, let's suppose an STG/WETH pool
2. Provide liquidity to the pool and mint LPs, let's suppose we mint ~1000$ worth of liquidity
3. Deposit the LP in an Arcadia account, the collateral is worth ~1000$
4. Send STG and WETH directly to the Aerodrome pool, let's suppose we send ~500_000$ worth of tokens
5. Call sync() on the Aerodrome pool
6. The pool reserves are increased and the collateral is now worth ~501_000$ use of any volatile Aerodrome pool LPs as collateral, as long as the underlying tokens are allowed.
An attacker can bypass the exposure limits set by a creditor.

## Recommendation
No recommendation available
