# [M] M-03 | Operators Could Replay Signatures In The Contract

## Summary
Severity: Medium
Contest weight: 0.1644
Dataset id: 2191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ProtocolVaultLedger contract relies on its backend to provide signatures for state‐changing functions, such as updateLPAndStrategyFund, allocatToFunds and similar functions, but it does not seem to enforce strict replay protection. Once a valid signature has been used, an operator can potentially reuse that same signature multiple times (even in different contexts) to reapply changes or to trigger previously authorized operations again within the same period. This opens the door for double handling of deposit/withdraw operations or other malicious state transitions. On the other hand, the vaultId is derived from the vault address and broker hash. All protocol vaults are deployed to the same address using CREATE3 and the brokerHash is a hardcoded value. As a result, the vaultIds of all protocol vaults across every EVM chain are identical and their accounting is tracked as a single account on the ledger chain. None of the signature verifications include the chain ID. Since vaultIds are identical across all chains, a valid signature on one chain will also be valid on another chain for the same periodId.

## Recommendation
Implement a nonce or sequential counter mechanism for each signature payload, incrementing a contract‐stored counter after each valid call. Moreover, consider adding chainIds to engine signatures.
