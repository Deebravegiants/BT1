# [M] Vault cap is not considered in the maxDeposit() calculations, which may make deposits fail

## Summary
Severity: Medium
Contest weight: 0.3597
Dataset id: 10562
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in the calculation of the maximum amount that can be deposited into a vault through the LoopStrategy contract. The maxDeposit() function returns a value based solely on the strategy’s internal parameters and the target utilization rate, but it completely ignores the hard cap that limits the total assets the vault may hold. This omission means that when the vault’s current balance is already close to its predefined cap, the function may still report a large allowable deposit amount. A user who follows the reported limit will attempt to send funds, but the vault’s internal cap check will reject the transaction, causing the deposit to revert. The root cause is a missing boundary check that should compare the remaining capacity (vaultCap − currentAssets) against the strategy‑derived limit and return the smaller of the two. The issue manifests only under conditions where the vault is nearly full and the utilization rate approaches the target, which are edge‑case scenarios that may not be exercised in routine testing. Affected parties include any depositor, liquidity providers, and the protocol itself because legitimate deposits are blocked, potentially reducing liquidity and preventing the system from reaching its intended utilization. The problem was discovered during a manual audit by ThreeSigma, where the logical flow of maxDeposit() was examined and the absence of a cap consideration was noted. It can be hard to notice because the function appears to work correctly for typical values and does not emit a specific error; the failure only occurs at runtime when the vault enforces its cap, resulting in a generic revert that may be mistaken for a network issue. From a user’s perspective the symptom is a failed transaction with no funds transferred, often described as “deposit failed” or “revert”, while the user’s balance remains unchanged. This class of bug is a missing boundary or cap enforcement check, a common accounting flaw where the contract’s view of available capacity diverges from the actual constraints. To remediate, the maxDeposit() implementation should be updated to incorporate the vault’s remaining capacity, returning the minimum of the strategy‑derived limit and the vault’s available space, thereby aligning the reported maximum with the true permissible deposit amount.

## Recommendation
Consider incorporating the maxDeposit() of the vault.
