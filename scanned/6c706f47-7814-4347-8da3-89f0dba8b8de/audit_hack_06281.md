# [H] Anyone can call migrate in Vault

## Summary
Severity: High
Reporter: psy4n0n
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L546
Type: audit-issue

## Details
# Anyone can call migrate in Vault

## Summary

The function `migrate` in `Vault` has access control issues and is callable by anyone. This can able be used to front-run `deactivate_migration` .

## Vulnerability Detail

The function `migrate` is defined as below:
```vyper
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
There is a missing check if `msg.sender` is `self.migration_admin` . 

## Impact

The bug can be used to call `migrate` even if admin doesn't want to migrate or if the admin tries to deactivate migration, a malicious user can front-run their transaction to call migrate.

## Code Snippet

```vyper
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

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L546

## Tool used

Manual Review

## Recommendation

Add the following check:
```vyper
assert msg.sender == self.migration_admin, "unauthorized"
```
