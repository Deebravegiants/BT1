# [M] Notional difference in AmmRouter:removeLiquidty() may revert in certain cases

## Summary
Severity: Medium
Contest weight: 0.0350
Dataset id: 10797
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the removeLiquidity function of the AMM router contract. When a liquidity provider attempts to withdraw liquidity, the function adjusts the remaining position by subtracting the long notional amount from the short notional amount if the net size of the position is positive, and performs the opposite subtraction when the net size is negative. This logic assumes that the long notional is always greater than the short notional for a positive size (or vice‑versa for a negative size). In reality the two notionals can be imbalanced; if the short notional exceeds the long notional while the size is positive, the subtraction yields a negative value that triggers a revert (or an under‑flow check). The root cause is the use of a signed difference instead of the absolute distance between the two notionals, leading to an arithmetic condition that is not universally true. An attacker or honest user can exploit this by creating a position where the short side is larger than the long side and then calling removeLiquidity with a positive size, causing the transaction to fail. The impact is that legitimate liquidity providers may be unable to withdraw their funds, resulting in stuck capital and a degraded user experience; from the protocol’s perspective, liquidity can become temporarily unavailable, breaking the expected accounting invariants. The issue manifests only when the notional imbalance crosses the sign boundary, so it may go unnoticed during normal operation where positions are balanced. It was discovered during a manual audit that examined the arithmetic of the router’s withdrawal logic. Because the code appears symmetric and the subtraction looks innocuous, developers might overlook the edge case where the subtraction order matters, making the bug subtle. To remediate, the contract should compute the absolute distance (the absolute difference) between the long and short notionals and adjust the position based on that value, ensuring that no negative intermediate results can occur regardless of which side is larger. This change restores the intended business rule that removing liquidity should never revert due to a simple notional imbalance, preserving the protocol’s accounting guarantees and allowing users to retrieve their expected balances.

## Recommendation
Use the distance between the notionals.
