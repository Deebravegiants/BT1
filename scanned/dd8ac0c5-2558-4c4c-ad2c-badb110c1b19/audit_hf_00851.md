# [M] M-11 | sUSD Wrapper Allows Burning Of All DebtShares

## Summary
Severity: Medium
Contest weight: 0.0957
Dataset id: 2588
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
sUSD can be minted from wrappers by depositing collateral such as USDe and receiving sUSD. An attacker could use these wrappers and the convertUSD function to burn all debtShares held by legacy market: sUSD convert -> snxUSD, snxUSD exchange swap -> USDe, USDe wrap -> sUSD, repeat. This would be problematic if most or all debt shares have been migrated, and were burnt through exploit described above. Then the leftover synths in the V2X system would be backed only by wrappers which traders cannot earn profit against (traders typically benefit from debt share value increase).

## Recommendation
Consider restricting convertUSD only to accounts which have migrated, and limiting conversion up to their migrated debt amount.
