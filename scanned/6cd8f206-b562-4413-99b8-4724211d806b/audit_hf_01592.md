# [M] In GReservePool, if a strategy is frozen reserve pool stops working

## Summary
Severity: Medium
Contest weight: 0.0987
Dataset id: 8549
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a strategy stops working it will become impossible to use the Reserve Pool. The functions deposit(), withdraw() and withdrawAll() will no longer work. This problem will also affect the contract glAVAX which will make the functions rebalance() and withdraw() not work as those functions can call the broken functions of the Reserve Pool. There is the possibility of the third party application that is being used by the strategy to stop working. Which will leave the funds in the third party application, making you wait for it to recover, and in the meantime the code will revert.

## Recommendation
It would be best in this scenario to remove strategies from the reserve pool (keeping them from reverting), this would be possible using the rebalance() function suggested in
