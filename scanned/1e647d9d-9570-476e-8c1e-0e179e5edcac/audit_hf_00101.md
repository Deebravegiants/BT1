# [M] M-30 | Validate Withdrawal Ignores Funding

## Summary
Severity: Medium
Contest weight: 0.1018
Dataset id: 194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _validateWithdrawalWithAction function uses either the available vault balance at init for the share price calculation or applies the PnL of the current price on it, whichever is less, but does not take funding into account.
Therefore if the vault paid funding fees to the longs between initiation and validation of a withdrawal the user receives more assets than the user should.
In certain edge cases this can also lead to a underﬂow DoS of the _validateWithdrawalWithAction function as this calculated withdrawal amount is later decreased from the _balanceVault where funding was applied to.

## Recommendation
Consider incorporating the latest vault funding into how many assets the users receives. Otherwise if this is acceptable to the protocol, be sure to document the behavior so that users are aware.
