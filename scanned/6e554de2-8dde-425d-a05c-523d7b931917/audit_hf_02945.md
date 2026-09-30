# [H] ClearingHouseLiq::_finalizeSubaccount() does not check if the subaccount has lps

## Summary
Severity: High
Contest weight: 0.2164
Dataset id: 16315
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ClearingHouseLiq::liquidateSubaccountImpl() can finalize an account, repaying the bad debt from insurance or socializing the account, depending on the amount of insurance available. It checks that the account has no positive balances, otherwise it may receive insurance or be socialized in some assets, increase its health and then retrieve the positive balances. However, it does not check if the subaccount has lps, which may be used to maliciously steal funds from insurance or via socialization of the debt. This can be exploited as the healh of the lp position should be lower than the real worth of the pro-rata base and quote assets, due to how the geometric mean works, which means that even if ClearingHouseLiq::liquidateSubaccountImpl() requires the account to be unhealthy at the end, the attacker will still profit later by burning the lp for the underlying amounts.

## Recommendation
In ClearingHouseLiq::_finalizeSubaccount(), revert if the subaccount has lp balances.
