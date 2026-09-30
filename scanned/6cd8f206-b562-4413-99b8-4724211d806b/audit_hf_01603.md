# [M] Centralization Risks, Especially Changes to Token Address Can Freeze Funds in Contract

## Summary
Severity: Medium
Contest weight: 0.1393
Dataset id: 8613
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Contracts are controlled by owners with privileged rights to perform administrative tasks, which requires trusting them not to make malicious updates. One potential risk is freezing funds in the contract by altering the LP token address.
Consider the following scenario:
• Users stake their LP/GUAN tokens, locking them in the veGuan contract.
• Over time, as the contract accumulates a significant amount of LP/GUAN tokens, the owner changes the LP token address to a worthless token.
• The owner then transfers this new, worthless LP token to the veGUAN contract.
• As a result, when users attempt to unstake, they receive the worthless LP token, losing their valuable GUAN tokens, which remain frozen.

Should the LP token address be changed any user unstaking would potentially receive a totally different token, with a different value to the original.
Other changes could impact how the protocol parameters are set, also changing the voting power of users.

## Recommendation
Consider adding a Timelock or/and using a multisig.
