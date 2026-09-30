# [M] M-09 | Same Address Controlled By Multiple Parties

## Summary
Severity: Medium
Contest weight: 0.1179
Dataset id: 1993
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The releaseOnEid function transfers the delegation rights to the beneficiary address on the origin chain. This means that the owner of the beneficiary address must be the same on both the origin and destination chain. If this is not the case one party is able to steal potential delegated airdrops, or the other party is unable to claim. In the case of multisig accounts across different chains, it is viable that contract addresses are not the same across different chains despite trading across EVM compatible chains.

## Recommendation
Delegated rights should not be granted from the Beacon contract immediately upon calling the releaseOnEid function. Instead the global delegation rights should only be granted on the origin chain after waiting for the releaseOnEid lifecycle to succeed, and then syncing the ownership state to the origin chain with the triggerOwnershipUpdate function. This way for those users who happen to control the smart contract at the beneficiary address on the destination chain, but not on the origin chain, they can preemptively delegate Shadow token rights on the destination chain to an address that they do control across all chains, preventing the inaccurate delegation on the origin chain.
