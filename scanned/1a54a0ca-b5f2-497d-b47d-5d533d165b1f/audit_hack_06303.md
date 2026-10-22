# [M] Vault deposits are not disabled if migration has been activated / executed

## Summary
Severity: Medium
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L198-L232
Type: audit-issue

## Details
# Vault deposits are not disabled if migration has been activated / executed

## Summary
Deposits remain enabled if migration has been activated, and even after execution.

## Vulnerability Detail
> Since vault potentially holds an Alchemix position over a long time during which changes at Alchemix could happen, the `migration_admin` has complete control over the vault and its position after giving depositors a 30 day window to liquidate (or transfer with a flashloan) their position if they're not comfortable with the migration.

During this 30 day window, and even after migration has been executed, the deposit flow may still work (depending if Alchemix disables deposits on their end).

## Impact
Deposits could theoretically still be possible during the 30 day window / after migration has been executed.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L198-L232

## Tool used
Manual Review

## Recommendation
To err on the side of caution, consider reverting if migration has been activated, or executed.
```vyper
# in register_deposit()
assert self.migration_active == max_value(uint256), "migration activated"
```
