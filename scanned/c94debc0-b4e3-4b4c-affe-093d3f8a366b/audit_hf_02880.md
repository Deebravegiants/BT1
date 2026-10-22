# [M] SideMarginFundingAccount: Unreachable functions changeAdminUser() and allocateFundingAccount()

## Summary
Severity: Medium
Contest weight: 0.5513
Dataset id: 16160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SideMarginFundingAccount constructor sets the ‘admin’ and ‘vault’ to the address of the sideVault. Since the sideVault can never call changeAdminUser() or allocateFundingAccount() these functions are out of reach.
The current implementation of the SideMarginFundingAccount constructor states:
```solidity
constructor (address _user, address _vault) {
    admin = msg.sender;
    user = _user;
    vault = _vault;
}
```
Since the sideVault deploys SideMarginFundingAccounts using the following line (line 321 in the code):
```solidity
SideMarginFundingAccount marginAccount = new SideMarginFundingAccount(user, address(this))
```
Both the 'admin' and the 'vault' will be set to the same address, i.e. the address of the sideVault.

## Recommendation
If the sideVault admin is the one supposed to call these functions, set that address as the SideMarginFundingAccount admin. If the user is the one supposed to call these functions, remove the variable 'admin' and give the user permission to call these functions. Also consider adding tests for these functions.
