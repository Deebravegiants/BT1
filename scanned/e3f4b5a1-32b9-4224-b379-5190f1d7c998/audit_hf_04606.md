# [M] M-39 | _getPairedTknAmt 0 Bond Slippage

## Summary
Severity: Medium
Contest weight: 0.0308
Dataset id: 22211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the LeverageManager contract where the internal function that bonds a user’s base token for a paired pToken is called with a hard‑coded slippage value of zero. Because the slippage parameter is fixed at zero, the contract does not enforce any minimum amount of pToken that must be received from the bonding operation. In practice, market conditions, price impact, or front‑running can cause the actual amount of pToken returned to be lower than the amount the user expects. Since the function does not check for this shortfall, the transaction completes successfully but the user ends up with fewer pTokens than anticipated, leading to a material loss of value when the position is later unwound or when the user expects a certain return. The issue manifests whenever a user initiates a bonding transaction through the LeverageManager, typically when opening a leveraged position or rebalancing assets. It affects all participants of the protocol who rely on the bonding mechanism, as their balances may be reduced without any explicit error. The problem was discovered during a manual security audit performed by the Guardian team, where the hard‑coded zero slippage was identified as a logical flaw that bypasses standard slippage protection. Because the transaction does not revert, the symptom is subtle: the UI may show a successful operation while the user’s pToken balance is unexpectedly lower, making the bug hard to notice without detailed balance checks. To remediate, the contract should expose a configurable slippage tolerance that the user can set, enforce a minimum acceptable pToken amount, and revert the transaction if the received amount falls below this threshold. This aligns the implementation with common slippage‑protection patterns and restores the expected accounting guarantees that the amount of pToken received should not be less than the user‑specified tolerance, preventing inadvertent loss of funds.

## Recommendation
Allow the user to input their slippage.
