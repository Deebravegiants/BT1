# [H] Migration logic is implemented incorrectly

## Summary
Severity: High
Reporter: ABA
Source: https://github.com/alchemix-finance/v2-foundry/blob/980f173ab1fe7458af8dc5907ecc8cbf74ae2b72/src/migration/MigrationTool.sol#L51
Type: audit-issue

## Details
# Migration logic is implemented incorrectly

## Summary

Migration logic is implemented incorrectly or incomplete

Project states that:
_`migration_admin`: can set a migration contract and after 30 day timelock execute a migration. In practice this role will be handed over to the Alchemix Multisig and would only need to be used in case something significant changes at Alchemix. Since vault potentially holds an Alchemix position over a long time during which changes at Alchemix could happen, the `migration_admin` has complete control over the vault and its position after giving depositors a 30 day window to liquidate (or transfer with a flashloan) their position if they're not comfortable with the migration. `migration_admin` works under the same security and trust assumptions as the Alchemix (Proxy) Admins._

__but there are no indications of this being the way to actually execute an `Alchemix` migration.__

## Vulnerability Detail

The entire migration for `Vault.vy` is executed via a call to the `migrate()` function

```Python
Migrator(self.migrator).migrate()
```

Where the `Migrator` interface has only the one method

```Python
interface Migrator:
    def migrate(): nonpayable
```

`self.migrator` would be presumably set to the _Alchemix Multisig_ with the expectation that a `migrate()` function would be found.

There is no evidente of such an interface existing
- this [alchemix documentation](https://alchemix-finance.gitbook.io/user-docs/how-to/migrate-between-vaults) mentions the procedure using their UI interface
- [Alchemix V2 Foundry](https://github.com/alchemix-finance/v2-foundry) underlying contract function for migration is [migrateVaults](https://github.com/alchemix-finance/v2-foundry/blob/980f173ab1fe7458af8dc5907ecc8cbf74ae2b72/src/migration/MigrationTool.sol#L51) from [MigrationTool.sol](https://github.com/alchemix-finance/v2-foundry/blob/master/src/migration/MigrationTool.sol) contract
```Solidity
    function migrateVaults(
        address startingYieldToken,
        address targetYieldToken,
        uint256 shares,
        uint256 minReturnShares,
        uint256 minReturnUnderlying
    ) external override returns (uint256) {
        // ...
    }
```
- no further documentation on [V2 Developer Docs](https://alchemix-finance.gitbook.io/v2/docs/alchemistv2?q=migrate) mentions it
- none of the [project multisigs](https://alchemix-finance.gitbook.io/user-docs/contracts#treasury) have the mentioned `migrate()` function 
    - [24H Timelock Multisig](https://etherscan.io/address/0x8392f6669292fa56123f71949b52d883ae57e225#readContract) 0x8392f6669292fa56123f71949b52d883ae57e225
    - [Developer Multisig](https://etherscan.io/address/0x9e2b6378ee8ad2a4a95fe481d63caba8fb0ebbf9#readProxyContract) 0x9e2b6378ee8ad2a4a95fe481d63caba8fb0ebbf9
- old, [deprecated V1 Alchemix](https://github.com/alchemix-finance/v2-foundry/blob/9c7818f986024f43c2b58a3a3bbcbfc4bd5bbcbf/src/interfaces/IAlchemistV1.sol) vaults had the [`migrate(IVaultAdapter _adapter)`](https://github.com/alchemix-finance/v2-foundry/blob/9c7818f986024f43c2b58a3a3bbcbfc4bd5bbcbf/src/interfaces/IAlchemistV1.sol#L8) function which is close, but still not relevant

## Impact

In case of a _required Alchemix Vault migration_, is not possible to migrate any leftover positions for users that do not manage to liquidate in time. This results in user funds loss.

This is also something the protocol itself decided to be cautious of.

## Code Snippet

[Migrator interface](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L86-L87)
```Python
interface Migrator:
    def migrate(): nonpayable
```

[Migration function](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L546-L556)
```Python
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

Seek help/guidance for migration with the `Alchemix` developers. At worst, implement the existing `migrateVaults` logic, even if it's not currently clear how such a migration would happen in the future. Sticking to known patterns may be enough in this case.
