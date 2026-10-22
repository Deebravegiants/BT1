# [M] The `settleCreditDeposit` function is incorrect.

## Summary
Severity: Medium
Contest weight: 0.5935
Dataset id: 11453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CreditDeposit (providers' profit) was counted twice in the vault debt.

https://github.com/Cyfrin/2025-01-zaros-part-2/blob/main/src/market-making/leaves/Market.sol#L443

```solidity
function settleCreditDeposit(Data storage self, address settledAsset, UD60x18 netUsdcReceivedX18) internal {
    // removes the credit deposit asset that has just been settled for usdc
    self.creditDeposits.remove(settledAsset);

    // calculate the usdc that has been accumulated per usd of credit delegated to the market
    UD60x18 addedUsdcPerCreditShareX18 = netUsdcReceivedX18.div(ud60x18(self.totalDelegatedCreditUsd));

    // add the usdc acquired to the accumulated usdc credit variable
    self.usdcCreditPerVaultShare =
        ud60x18(self.usdcCreditPerVaultShare).add(addedUsdcPerCreditShareX18).intoUint128();

    // deduct the amount of usdc credit from the realized debt per vault share, so we don't double count it
    self.realizedDebtUsdPerVaultShare = sd59x18(self.realizedDebtUsdPerVaultShare).sub(
        addedUsdcPerCreditShareX18.intoSD59x18()
    ).intoInt256().toInt128();
}
```

```solidity
function getVaultAccumulatedValues(
    ...
)
    internal
    view
    returns (
        SD59x18 realizedDebtChangeUsdX18,
        SD59x18 unrealizedDebtChangeUsdX18,
        UD60x18 usdcCreditChangeX18,
        UD60x18 wethRewardChangeX18
    )
{
    ...
    realizedDebtChangeUsdX18 = !lastVaultDistributedRealizedDebtUsdPerShareX18.isZero()
        ? sd59x18(self.realizedDebtUsdPerVaultShare).sub(lastVaultDistributedRealizedDebtUsdPerShareX18).mul(
            vaultCreditShareX18.intoSD59x18()
        )
        : SD59x18_ZERO;
    ...
    usdcCreditChangeX18 = !lastVaultDistributedUsdcCreditPerShareX18.isZero()
        ? ud60x18(self.usdcCreditPerVaultShare).sub(lastVaultDistributedUsdcCreditPerShareX18).mul(
            vaultCreditShareX18
        )
        : UD60x18_ZERO;
    ...
}
```

The CreditDeposit was counted in both of realizedDebtChangeUsdX18 and usdcCreditChangeX18.

```solidity
Vault.sol
function _recalculateConnectedMarketsState(
    Data storage self,
    uint128[] memory connectedMarketsIdsCache,
    bool shouldRehydrateCache
)
    private
    returns (
        uint128[] memory rehydratedConnectedMarketsIdsCache,
        SD59x18 vaultTotalRealizedDebtChangeUsdX18,
        SD59x18 vaultTotalUnrealizedDebtChangeUsdX18,
        UD60x18 vaultTotalUsdcCreditChangeX18,
        UD60x18 vaultTotalWethRewardChangeX18
    )
{
    ...
    for (uint256 i; i < connectedMarketsIdsCache.length; i++) {
        ...
        if (!ctx.marketUnrealizedDebtUsdX18.isZero() || !ctx.marketRealizedDebtUsdX18.isZero()) {
            // distribute the market's debt to its connected vaults
            market.distributeDebtToVaults(ctx.marketUnrealizedDebtUsdX18, ctx.marketRealizedDebtUsdX18);
        }
        ...
        if (!market.getTotalDelegatedCreditUsd().isZero()) {
            ...
            (
                ctx.realizedDebtChangeUsdX18,
                ctx.unrealizedDebtChangeUsdX18,
                ctx.usdcCreditChangeX18,
                ctx.wethRewardChangeX18
            ) = market.getVaultAccumulatedValues(
                ud60x18(creditDelegation.valueUsd),
                sd59x18(creditDelegation.lastVaultDistributedRealizedDebtUsdPerShare),
                sd59x18(creditDelegation.lastVaultDistributedUnrealizedDebtUsdPerShare),
                ud60x18(creditDelegation.lastVaultDistributedUsdcCreditPerShare),
                ud60x18(creditDelegation.lastVaultDistributedWethRewardPerShare)
            );
        }
        ...
    }
}
```

```solidity
function recalculateVaultsCreditCapacity(uint256[] memory vaultsIds) internal {
    for (uint256 i; i < vaultsIds.length; i++) {
        ...
        (
            uint128[] memory updatedConnectedMarketsIdsCache,
            SD59x18 vaultTotalRealizedDebtChangeUsdX18,
            SD59x18 vaultTotalUnrealizedDebtChangeUsdX18,
            UD60x18 vaultTotalUsdcCreditChangeX18,
            UD60x18 vaultTotalWethRewardChangeX18
        ) = _recalculateConnectedMarketsState(self, connectedMarketsIdsCache, true);
        ...
        if (!vaultTotalRealizedDebtChangeUsdX18.isZero()) {
            self.marketsRealizedDebtUsd = sd59x18(self.marketsRealizedDebtUsd).add(
                vaultTotalRealizedDebtChangeUsdX18
            ).intoInt256().toInt128();
        }
        ...
        if (!vaultTotalUsdcCreditChangeX18.isZero()) {
            self.depositedUsdc = ud60x18(self.depositedUsdc).add(vaultTotalUsdcCreditChangeX18).intoUint128();
        }
        ...
    }
}
```

The CreditDeposit was counted in both of vaultTotalRealizedDebtChangeUsdX18 and vaultTotalUsdcCreditChangeX18.

```solidity
function getUnsettledRealizedDebt(Data storage self)
    internal
    view
    returns (SD59x18 unsettledRealizedDebtUsdX18)
{
    unsettledRealizedDebtUsdX18 =
        sd59x18(self.marketsRealizedDebtUsd).add(unary(ud60x18(self.depositedUsdc).intoSD59x18()));
}
```

The CreditDeposit was counted twice in the getUnsettledRealizedDebt.

The vault's debt calculation was incorrect.  
Incorrect accounting results in losses for users.

## Recommendation
Consider counting the CreditDeposit in either usdcCreditPerVaultShare or realizedDebtUsdPerVaultShare.

Low Risk Findings
