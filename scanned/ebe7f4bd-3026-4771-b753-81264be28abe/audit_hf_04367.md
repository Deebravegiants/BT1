# [H] H-05 | Missing whenNotPaused Modifier Causes Loss Of Funds

## Summary
Severity: High
Contest weight: 0.2269
Dataset id: 21572
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Several contracts in the repository inherit Pausable from OpenZeppelin and correctly implement the pause and unpause functions. However, the modifier whenNotPaused is not implemented in core contracts such as OrderOFT, OrderAdapter and ProxyLedger. The modifier should be added to user-facing functions to allow the owner to pause operations in the event of an emergency for example. A more critical issue also exists because OmnichainLedgerV1 correctly implements the whenNotPaused modifier while ProxyLedger does not. If the owner were to pause both contracts, users would still be able to call functions like stake on the ProxyLedger which would execute successfully but revert on destination chain. User's tokens would lose funds as their tokens would be burned on source chain, minted on destination chain but never staked on the user's behalf.

## Recommendation
Add modifier whenNotPaused to core functions such as send, stake, and sendUserRequest.
