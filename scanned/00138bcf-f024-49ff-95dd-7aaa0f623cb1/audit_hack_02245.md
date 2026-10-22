# [M] H-09 Unmitigated

## Summary
Severity: Medium
Source: https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L963
Type: audit-issue

## Details
# Lines of code




# Vulnerability details

### Issue not mitigated

### About the problem
In the report i have described some vaults that will not work in the designed system. Example of such vault will be any vault that has withdraw limit. In this case `_yieldVault.maxWithdraw` call [will not return actual amount of assets](https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L963) in the underlying vault and because of that, vault will become undercollateralized.
Another example of vaults that will not work are vaults that take fees. Such vaults will become undercollateralized at first deposit.

I didn't see that protocol has acknowledged issue(it looks like they tried to fix it) and i don't see how it's possible to fix this issue in the code, looks like the only option currently is to not create Vaults with some specific underlying vaults, that has withdraw limit or other restrictions.

### Solution
Need to have a list of protocols that will not work.
