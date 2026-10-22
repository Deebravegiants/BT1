# [M] GLOBAL-3 | Eigen Airdrop Cannot Be Claimed

## Summary
Severity: Medium
Contest weight: 0.0349
Dataset id: 20581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing claim mechanism for EigenLayer airdropped tokens that are allocated to users who have staked liquidity staking tokens (LSTs) through the Rest Vault. The root cause is that the Rest Vault contracts do not implement any function or workflow that allows a user to withdraw or claim the airdropped tokens after the distribution event. Because the contract lacks this functionality, a user who is shown as eligible for the airdrop in the UI will attempt to claim the reward but receives no tokens and sees no change in their balance. This situation can be reproduced whenever an airdrop is announced and the Rest Vault holds the allocated tokens; under those conditions the claim transaction either reverts or silently does nothing because there is no code path to transfer the tokens to the caller. The impact is that users lose the expected benefit of the airdrop, effectively causing funds to remain locked in the contract with no way to retrieve them, which undermines trust in the protocol’s incentive mechanisms and breaks accounting assumptions that airdropped rewards will be distributed. The issue was discovered during a systematic audit of the Rest Vault’s public interfaces, where the auditor noted that while eligibility checks exist, no corresponding withdrawal or claim function is present, a discrepancy that can be easy to miss because the contract may still compile and operate correctly for its core staking logic. From a user’s perspective the symptom is a mismatch between the displayed eligibility (“you can claim X tokens”) and the actual outcome (balance stays the same, no transaction receipt of tokens). The bug belongs to the class of “missing reward distribution logic” or “incomplete claim flow” vulnerabilities, where business logic assumes a transfer will occur but the implementation does not provide the necessary code. To remediate the issue the contract should be extended with a secure claim or withdraw function that transfers the airdropped tokens to the rightful staker, and the contract architecture should allow for future upgrades so that similar omissions can be patched without redeploying the entire system. Adding this functionality restores the intended economic incentive, aligns on‑chain accounting with off‑chain expectations, and prevents users from experiencing silent loss of rewards.

## Recommendation
Consider adding the functionality to withdraw airdropped tokens and/or make the contracts upgradeable.
