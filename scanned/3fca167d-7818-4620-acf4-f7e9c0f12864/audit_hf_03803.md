# [M] It may be possible to liquidate on behalf of

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 20016
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the caller of any liquidation action is the vault itself, there is no validation of the liquidator parameter and therefore, any arbitrary account may act as the liquidator if they have approved any amount funds for the VaultLiquidationAction.sol contract.

While the vault implementation itself should most likely handle proper validation of the parameters provided to actions enabled by the vault, the majority of important validation should be done within the Notional protocol. The base implementation for vaults does not seem to sanitise liquidator and hence users could deleverage accounts on behalf of a liquidator which has approved Notional contracts.

```solidity
function _authenticateDeleverage(
    address account,
    address vault,
    address liquidator
) private returns (
    VaultConfig memory vaultConfig,
    VaultAccount memory vaultAccount,
    VaultState memory vaultState
) {
    // Do not allow invalid accounts to liquidate
    requireValidAccount(liquidator);
    require(liquidator != vault);

    // Cannot liquidate self, if a vault needs to deleverage itself as a whole it has other methods
    // in VaultAction to do so.
    require(account != msg.sender);
    require(account != liquidator);

    vaultConfig = VaultConfiguration.getVaultConfigStateful(vault);
    require(vaultConfig.getFlag(VaultConfiguration.DISABLE_DELEVERAGE) == false);

    // Authorization rules for deleveraging
    if (vaultConfig.getFlag(VaultConfiguration.ONLY_VAULT_DELEVERAGE)) {
        require(msg.sender == vault);
    } else {
        require(msg.sender == liquidator);
    }

    vaultAccount = VaultAccountLib.getVaultAccount(account, vaultConfig);

    // Vault accounts that are not settled must be settled first by calling settleVaultAccount
    // before liquidation. settleVaultAccount is not permissioned so anyone may settle the account.
    require(block.timestamp < vaultAccount.maturity, "Must Settle");

    if (vaultAccount.maturity == Constants.PRIME_CASH_VAULT_MATURITY) {
        // Returns the updated prime vault state
        vaultState = vaultAccount.accruePrimeCashFeesToDebtInLiquidation(vaultConfig);
    } else {
        vaultState = VaultStateLib.getVaultState(vaultConfig, vaultAccount.maturity);
    }
}
```

A user may be forced to liquidate an account they do not wish to purchase vault shares for.

## Recommendation
Make the necessary changes to BaseStrategyVault.sol or _authenticateDeleverage(), whichever is preferred.
