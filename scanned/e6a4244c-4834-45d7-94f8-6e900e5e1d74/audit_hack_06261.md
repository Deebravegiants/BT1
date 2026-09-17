# [M] Migration can not perform any meaningful actions

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L513-L556
Type: audit-issue

## Details
# Migration can not perform any meaningful actions

## Summary

Migration contract wont be able to perform any meaningful actions due to not having access to Vault assets.

## Vulnerability Detail

The `Vault.migrate` function performs a call to `Migrator(self.migrator).migrate()` which then is supposed to perform all migration actions. However, the migrator is never given approval to perform any actions in place of the vault (e.g. transfering debt shares):

```py
@external
def activate_migration(_migrator_addr: address):
    """
    @notice
        Sets a migration contract and starts the 30 day timelock before
        migration can be performed.
        Can only be called by the migration_admin.
    """
    assert msg.sender == self.migration_admin, "unauthorized"
    assert self.migrator == empty(address), "cannot override active migration"
    assert _migrator_addr != empty(address), "cannot set migrator to zero address"

    self.migrator = _migrator_addr
    self.migration_active = block.timestamp + MIGRATION_TIMELOCK
    self.migration_executed = False

    #@done-audit-issue lack of approvals? or maybe supposed to be a delegatecall?
    log MigrationActivated(_migrator_addr, self.migration_active)

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

Due to significant changes of Alchemix being relatively unlikely, I deem the severity to be medium. 
## Impact

Migration can not be performed.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L513-L556

## Tool used

Manual Review

## Recommendation

Either approve the transfer of all relevant assets (e.g. debt shares and maybe WETH) or perform a delegatecall to the migrator instead, so that migration code can be executed in the context of the vault.
