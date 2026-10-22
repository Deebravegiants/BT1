# [M] BRF-2 | Unbounded disRate

## Summary
Severity: Medium
Contest weight: 0.0374
Dataset id: 4056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unbounded distribution rate (disRate) that can be set to any value through the setDisRate function without any upper limit. Because the distribute function uses this rate to calculate how much of a supplied amount should be transferred, a disRate greater than 100 % (or the logical maximum of 57 % as intended by the protocol) causes the contract to allocate more tokens than were actually provided. The root cause is the lack of a constraint on the disRate variable, allowing it to be increased arbitrarily by whoever can call setDisRate. An attacker who can modify disRate – either through ownership, a compromised admin key, or a governance exploit – can set an excessively high rate and then trigger distribute, causing the contract to debit more funds than it holds. This leads to a net loss of assets for the protocol, potentially draining its reserves and leaving legitimate users with missing or zero balances when they later request withdrawals or refunds. The issue manifests whenever setDisRate is called with a value above the intended cap and a subsequent distribute call is made; it may remain unnoticed because the contract does not check for balance underflow or emit warnings when the calculated distribution exceeds the available pool. From a user’s perspective, a user may expect to receive a proportional payout but either sees an unexpectedly large credit (which later disappears when the pool is exhausted) or, more commonly, later users receive nothing because the pool has been depleted. The bug belongs to the class of unchecked parameter bounds leading to accounting errors and over‑allocation. It was discovered during a manual audit that highlighted the missing cap on disRate. To remediate, the contract should enforce a maximum disRate (for example 57 % or 1/1.75) and include sanity checks that the calculated distribution does not exceed the contract’s current balance before performing the transfer, thereby preserving accounting integrity and preventing fund loss.

## Recommendation
Implement a maximum cap for disRate. A cap of ~ 57% (1/1.75) would allow for a maximum distribution of amount.
