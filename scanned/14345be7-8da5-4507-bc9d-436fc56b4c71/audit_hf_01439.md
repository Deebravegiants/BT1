# [H] withdrawRewards() does not accumulate the rewards for all the space ids, leading to lost rewards

## Summary
Severity: High
Contest weight: 0.0332
Dataset id: 7457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the reward withdrawal routine that processes an array of space identifiers. The function iterates over each supplied space ID, calls an internal routine to compute the reward for that ID, and stores the result in a local variable named reward. However, the implementation uses a simple assignment operator (=) instead of an accumulation operator (+=) inside the loop. As a result, each iteration overwrites the previously calculated amount, so only the reward from the last processed space ID is actually transferred to the caller. This logical error occurs whenever a user invokes withdrawRewards with more than one space ID, which is a common scenario for participants who hold multiple positions in the protocol. Users expect the function to sum all pending rewards and deliver the total amount, but they receive only a partial payout, effectively losing the rewards associated with earlier IDs. From the user’s perspective the UI may show a successful transaction while the displayed balance or received amount is lower than expected, leading to confusion or the impression that funds have vanished. The issue was uncovered during a manual audit of the contract’s reward accounting logic, where the auditor noticed that the reward variable was reset on each loop iteration. The bug is subtle because the function behaves correctly for a single ID, so basic tests that only cover one‑element arrays do not reveal the problem. The root cause is a missing arithmetic accumulation operator, a classic example of an “incorrect state update” or “reward aggregation” bug. To remediate the flaw the assignment should be replaced with an addition assignment (reward += _withdrawRewards(spaceIds[i])) so that the total reward is correctly summed before the final transfer. This change restores the intended business logic that rewards are additive across all owned space IDs and prevents inadvertent loss of funds.

## Recommendation
Replace = by +=.
