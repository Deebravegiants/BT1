# [M] VaultHelper deposits don't work with fee-on transfer tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

cmichel


# Vulnerability details

There are ERC20 tokens that may make certain customizations to their ERC20 contracts.
One type of these tokens is deflationary tokens that charge a certain fee for every `transfer()` or `transferFrom()`.
Others are rebasing tokens that increase in value over time like Aave's aTokens (`balanceOf` changes over time).


## Impact
The `VaultHelper`'s `depositVault()` and `depositMultipleVault` functions transfer `_amount` to `this` contract using `IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);`.
This could have a fee, and less than `_amount` ends up in the contract.
The next actual vault deposit using `IVault(_vault).deposit(_token, _amount);` will then try to transfer more than the `this` contract actually has and will revert the transaction.

## Recommended Mitigation Steps
One possible mitigation is to measure the asset change right before and after the asset-transferring routines.
This is already done correctly in the `Vault.deposit` function.
