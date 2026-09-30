# [M] Just-in-Time depositor can take interests with-

## Summary
Severity: Medium
Contest weight: 0.1219
Dataset id: 20216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SPs pay the protocol interests via the pay function. The depositor can monitor mempool for pay call transactions and steal the interests with sandwich attack. The attacker monitors the mempool for pay transactions and can launch the following sandwich attack.
1. Frontrun with a transaction that deposits a large amount of assets to InfinityPool. This will mints the attacker a large amount of iFIL shares.
2. The pay transaction gets executed and the interests are distributed to depositors. The attack will get a large portion of the interests because he holds a large amount of the iFIL shares.
3. Backrun with a withdraw transaction to exit and profit. The attacker can steal a large portion of the protocol income. The severity is set to high because this is an ongoing impact and will render the protocol useless for depositors.

## Recommendation
Add a lock period from deposit to withdraw.
