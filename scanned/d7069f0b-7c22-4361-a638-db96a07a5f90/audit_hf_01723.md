# [M] Game design is vulnerable to block stuffing attacks

## Summary
Severity: Medium
Contest weight: 0.1718
Dataset id: 9389
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor (miner or player) can execute a block stuffing attack to gain an unfair advantage in the game by preventing other users from interacting with the contract. Attack Scenario: 1. The game starts at t = 0 with a pot of $1000. 2. Countdown = 300 seconds, decrement = 30 seconds and minimum countdown = 60 seconds. 3. The attacker alternates button presses between two controlled addresses (e.g., Player A and Player B), reducing the countdown to 60 seconds (countdownMinimum). 4. Once the countdown is at 60 seconds, the attacker initiates a block stuffing attack to fill all blocks with high-gas transactions for the next 60 seconds. 5. As a result, no other players can interact with the contract, and the attacker becomes the winner by default. Block stuffing effectively censors legitimate interactions and ensures only the attacker's transactions are included. Cost Consideration: On Optimism, the cost to stuff a full block for one minute is currently around $169 (based on a gas price of 5.46 Gwei and block gas limit of 35,000,000). Thus, the attack becomes profitable when the potential reward (pot size) exceeds the attack cost. References: - The Anatomy of a Block Stuffing Attack

## Recommendation
As game can only be ended by a trusted user, this won't be a problem for now. But might be a problem when prize claiming process will also become permission-less.
