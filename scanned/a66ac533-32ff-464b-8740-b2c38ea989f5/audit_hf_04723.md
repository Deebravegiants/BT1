# [M] WETH was never set in baseLeverageExecu-

## Summary
Severity: Medium
Contest weight: 0.0302
Dataset id: 22531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an uninitialized WETH address variable in the baseLeverageExecutor contract. Because the constructor never assigns a real WETH contract address, the variable retains its default value of address zero. Any function that attempts to wrap or unwrap Ether by calling the WETH contract therefore targets the zero address, causing external calls to fail. This situation arises whenever a user interacts with leverage or settlement logic that relies on WETH, for example when depositing ETH to be wrapped, withdrawing wrapped ETH, or performing a leveraged trade that requires WETH conversion. From the user’s perspective the transaction reverts or completes without moving funds, leading to symptoms such as “my balance stays at zero after I tried to deposit ETH” or “the refund I expected never arrives”. The root cause is a missing initialization step in the contract’s constructor, a logical oversight that compiles without error because Solidity assigns zero to uninitialized address variables. The bug is hard to notice in static analysis because the code compiles and the variable is syntactically correct; the failure only manifests at runtime when the WETH interface is invoked. Exploitation does not require malicious intent; simply calling any WETH‑dependent function triggers a revert, effectively creating a denial‑of‑service condition for all participants. The impact is that users cannot wrap or unwrap ETH, potentially locking funds or preventing expected financial operations, which violates the protocol’s accounting assumptions that ETH can be converted to WETH on demand. The issue was discovered during a manual audit that reviewed contract initialization patterns. To remediate, the WETH state variable should be set to the correct WETH contract address in the constructor or via an explicit initializer function, ensuring that all WETH interactions target a valid contract and restoring the intended financial flow.

## Recommendation
initialize the WETH state Var via the constructor.
