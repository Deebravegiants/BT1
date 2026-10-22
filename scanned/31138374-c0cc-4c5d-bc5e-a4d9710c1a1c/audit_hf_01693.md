# [H] MJR-2 Possible ddos attack

## Summary
Severity: High
Contest weight: 0.0143
Dataset id: 9272
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a front‑running price manipulation in the withdraw() function of the staking rewards contract. The contract calculates a user’s reward based on the current pool price at the moment withdraw is called. Because the price is derived from mutable pool state that can be altered by any participant before the withdraw transaction is mined, a malicious actor can submit a transaction that changes the price just before the victim’s withdraw is executed. By doing so the attacker forces the price to a value that reduces the computed reward to zero or a negligible amount, causing the legitimate staker to receive no rewards despite having accrued them. This attack can be carried out whenever a user initiates a withdrawal and the network’s transaction ordering allows the attacker to place a preceding transaction, i.e., under normal Ethereum mempool conditions. The affected parties are stakers who expect to receive proportional rewards; they see their balance unchanged or a missing reward after the transaction. The issue was discovered during a manual audit of the StakingRewardsV3 contract, where the price‑dependent reward logic was identified as relying on a single instantaneous pool price without any smoothing or averaging. Because the price can be moved by a single transaction, the problem may not be obvious from static analysis; it only manifests when an attacker deliberately reorders transactions, making it hard to detect without dynamic testing. The bug belongs to the class of oracle manipulation or front‑running vulnerabilities where on‑chain state used for accounting can be tampered with by adversaries. From a user’s perspective the UI shows a successful withdrawal but the reward amount displayed is zero, contradicting the expectation that the user receives their earned tokens. The business logic that rewards are proportional to the time‑weighted average price is violated, breaking accounting guarantees. A proper mitigation is to compute the price using an average over a recent block window or a time‑weighted moving average, or to use a trusted external price oracle, thereby preventing a single transaction from drastically shifting the price used for reward calculation. Implementing such an averaging mechanism removes the ability for an attacker to front‑run the withdraw and ensures that rewards are calculated on a stable price reference.

## Recommendation
We recommend to get an average price for this check.
