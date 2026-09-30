# [H] LCY-1 | Incorrect GMI Attribution

## Summary
Severity: High
Contest weight: 0.3763
Dataset id: 20510
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The global state variable vaultGmiAttribution represents the exact amount of GMI attributed to each vault. Throughout the codebase it is repeatedly set using the _commitGmiDeltaProportions function from the LibCycle library. This function incorrectly uses the vaultGmiAttribution values as percentages, which they are not, instead of absolute values. Because of this, the prevAmounts are extremely large and any _amt being added to will be minuscule in comparison which leads to almost 0% change in the proportions. The larger the amount is, the more the allocations will deviate from the intended values.

A direct, severe issue, appears during a rebalance when internally swapping GMI for native assets for internally settable differences between the 2 vaults. After swapping native tokens (L146-L152) the new allocations need to be saved from each vault, removing GMI from one vault and adding to another (L156-L172).

Since the call to _commitGmiDeltaProportions results in no practical change in the percentage, users are directly losing funds via depreciation of vault shares, since ETH will be swapped in these cases but GMI attribution has not changed.

To illustrate the impact, consider the following scenario:
Total GMI valuation of $6 million
Initial vault GMI allocation: 57% (57.0000090250015061%) USDC vault and 43% (42.9999909749984939%) WETH vault an amount approx $300K GMI (5% of GMI amount) is needed be moved from one vault to another

In this case, the current, incorrect implementation shows that the vault allocation, after adding the new amount, is: USDC: 57% (57.0000095000015852%), ETH: 43% (42.9999904999984147%). The new amount impact is erased and $300K worth of ETH is not GMI attributed.

If the correct implementation would be used, the resulting allocations are USDC: 60% (60.0000095000015853%), ETH: 40% (39.9999904999984146%). The error in this case is an absolute 3% value in allocation.

## Recommendation
Modify the _commitGmiDeltaProportions to correctly work with and save the values as absolute amounts.
