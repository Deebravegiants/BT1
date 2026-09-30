# [H] H-04 | Order Creation And Execution Can Be DoSed

## Summary
Severity: High
Contest weight: 0.3114
Dataset id: 2412
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
New positions are added to the positionTickRangeList array. This array can be artificially bloated, causing a DOS to new order creation or existing order execution. Upon creating an order for a new position or executing an existing position, the positionTickRangeList must be reordered, i.e. the array indexes must be moved around. A malicious user can create many scale orders or range limit orders to inflate the size of the array which will cause out-of-gas reverts when a legitimate user attempts to create an order at a new position or a swap attempts to execute an order. Essentially, all swaps through the pool will revert. The attacker is able to recoup all of the funds used to set up the positions by cancelling them. Furthermore, an oversight in the position removal logic allows these spam positions to stay permanently without possibility of removal. Note: Through testing, it was determined that scale orders could be spammed to create enough positions so that a single order execution would cost ~15,000,000 gas, while the estimated block gas limit is 30,000,000. Range limit orders could be used to fill up the array more to achieve the full OOG, though this is not performed in the POC.

## Proof of Concept
https://gist.github.com/fatherGoose1/6f2c3251292138a1c6cf99dcebabc732

## Recommendation
Make sure when the attacker cancels a limit order, this call to also remove the created position if his order was the only one for this position. This would make the attack more expensive but still possible since he will not be able to retrieve his funds and hold the DOS at the same time. To prevent the issue from happening involves a design decision from the team either to limit the amount of positions that can be opened at the same time or to seek a different method of storing and identifying executable positions.
