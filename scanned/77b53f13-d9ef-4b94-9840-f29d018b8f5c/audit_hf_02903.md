# [C] UB-1 | Total Bets Not Updated

## Summary
Severity: Critical
Contest weight: 0.0795
Dataset id: 16205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an accounting error where the contract’s internal record of total bets per side is never updated when a user places a bet. The root cause is that the placeBet function does not modify the bets mapping, leaving the stored total for each side unchanged at zero. When a user later calls withdrawGain, the function attempts to calculate the payout by dividing the total reward pool by bets[result.winner]. Because bets[result.winner] remains zero, the division operation triggers a division‑by‑zero exception, causing the transaction to revert. An attacker or any participant can exploit this by simply invoking withdrawGain after a round has been resolved; the call will always fail, preventing any payout from being transferred. The impact is that all funds locked in the betting pool become unrecoverable through the contract’s intended withdrawal path, effectively resulting in a total loss of user deposits. This condition occurs every time a round finishes, regardless of which side wins, because the total bets are never recorded. All users who have placed bets, as well as the protocol that relies on the betting mechanism, are affected. The issue was discovered during a manual audit that inspected state updates and identified that the bets mapping was never incremented. Because the contract does not emit explicit error messages for the division‑by‑zero case, the failure may appear as a generic revert, making it hard to diagnose without reviewing the source. The proper fix is to update the bets mapping inside placeBet, for example by adding bets[_side] += betAmount, ensuring that the total amount wagered on each side reflects the actual deposits. Conceptually, this belongs to the class of state‑inconsistency bugs that lead to arithmetic exceptions and broken accounting logic. From a user’s perspective the UI would show a successful bet placement, but later the withdrawal button would either do nothing or revert, and the user would see a zero payout despite having won, violating the expectation that a winning bet yields a reward. The bug breaks the fundamental business rule that the sum of bets determines the share of the reward pool, causing money to disappear from the contract’s accessible balance.

## Recommendation
In placeBet, increment the bets mapping with bets[_side] += betAmount.
