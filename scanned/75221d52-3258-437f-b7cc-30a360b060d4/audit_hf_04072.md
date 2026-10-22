# [H] GMIU-1 | Entire Misallocation Covered On Deposit Or Withdrawal

## Summary
Severity: High
Contest weight: 0.2705
Dataset id: 20525
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the adjustToBalance function when the shareValue is insufficient to cover the entire underAllocation, the difference array with the entire positive underAllocations is returned. However, the shareValue is insufficient to cover these underAllocation amounts. As a result, whenever a share amount is minted that is unable to cover the entire underAllocation, the entire underAllocation amounts will be charged to the caller while only remunerating the caller with the insufficient share amount that was specified.

This issue is most clearly demonstrated with a mint of a single wei. The single wei will be insufficient to cover the entire underAllocation, as a result, the caller is errantly required to provide the entire underAllocation amount in GM tokens to mint the specified single wei of GMI.

Similarly, this issue is present with withdrawals, where redeeming a single wei of shares will result in the withdrawer receiving the entire over-allocation amount.

This is a fundamental accounting error and will significantly affect the assetVault share values and the GMI valuation over time.

## Recommendation
Replace the return statement on line 72 with:
Solarray.arrayAddProportion(toBalanceAmount, shareValue, difference, underAllocation, true);
