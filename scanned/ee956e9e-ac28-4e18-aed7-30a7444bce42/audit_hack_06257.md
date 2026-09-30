# [M] Vault's migration contract can't really migrate anything

## Summary
Severity: Medium
Reporter: Ruhum
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L545-L556
Type: audit-issue

## Details
# Vault's migration contract can't really migrate anything

## Summary
The migration contract is not approved to modify the vault's position on Alchemix. The contract won't be able to migrate any of the funds.

## Vulnerability Detail
The migration contract isn't granted any approvals to manage the position on Alchemix. It won't be able to access its funds. Neither is the contract called through a `delegatecall` so that it can execute arbitrary logic for the Vault contract. The migration contract won't be able to access any of the vault's funds and thus won't be able to complete a migration.

Effectivelly, this feature is useless.

## Impact
In case of a change to Alchemix, the planned migration won't be successful. Funds will be locked up.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L545-L556
```python
@external
def migrate():
    """
    @notice
        Calls migrate function on the set migrator contract.
        This is just in case there are severe changes in Alchemix that
        require a full migration of the existing position.
    """
    assert self.migration_active <= block.timestamp, "migration not active"
    assert self.migration_executed == False, "migration already executed"
    self.migration_executed = True
    Migrator(self.migrator).migrate()

```
## Tool used

Manual Review

## Recommendation
The easiest solution is to use `delegatecall` to execute arbitrary logic when calling the `migrate()` function.
