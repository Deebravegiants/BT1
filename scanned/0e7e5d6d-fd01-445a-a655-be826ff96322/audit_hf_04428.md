# [M] M-04 | Incorrect Virtual Reserves Accounting

## Summary
Severity: Medium
Contest weight: 0.1266
Dataset id: 21904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the launch function the pessimisticCapacity includes the floor reserves when stretching the virtual reserves over the entire floor position to compute its worst case capacity. This incorrectly accounts for stretching out the floor reserves which would actually increase if the price were to rise to the upper floor tick. This was the original reason why the virtual reserves had to be stretched because they would not receive corresponding reserves in as price rose to the upper tick of the floor. This accounting is attempted to be fixed by leaving the bAssets of the floor position in the circulating supply, as if they had been swapped out of the floor as price rose. However this again does not account for the reserves of the floor increasing due to swap input amounts.

## Recommendation
Remove the special accounting for the floor position and revert to the original solvency check that was previously present in the launch function, with the one addition of the LOOPS.totalDebt() value in the pessimisticCapacity accounting.
