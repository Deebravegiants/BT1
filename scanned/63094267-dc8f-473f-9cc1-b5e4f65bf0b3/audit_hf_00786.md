# [C] C-04 | Drain All Pools With SuperPool As Collateral

## Summary
Severity: Critical
Contest weight: 0.2717
Dataset id: 2514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SuperPool vault shares should have the same decimals as the underlying ASSET. The decimal value is set in the constructor. However, this is not the case, as depositing 1e18 assets will give you 1e36 shares. The issue relies on _convertToShares when the first user deposits, where lastTotalAssets and totalSupply are 0, but it will multiply by 10 ** DECIMALS:
shares = assets.mulDiv(totalSupply() + 10 ** DECIMALS, lastTotalAssets + 1, rounding);
Although users will be able to redeem the shares for the correct amount of tokens, there is a discrepancy between the decimals() of the vault and the minted share units. Users will be able to use this vault token as collateral to borrow assets against. When calculating the asset value of the vault token in RiskModule, the value returned will be 1e18 times greater than expected. Therefore, users will be able to drain pools by borrowing all assets, as the collateral value is basically infinite: vaultTokens(1e36) * priceInEth(1e18) / decimals(1e18) = 1e36 ether value

## Recommendation
Implement the following:
• shares = assets.mulDiv(totalSupply() + 10 ** DECIMALS, lastTotalAssets + 1, rounding);
• shares = assets.mulDiv(totalSupply() + 1, lastTotalAssets + 1, rounding);
• assets = shares.mulDiv(lastTotalAssets + 1, totalSupply() + 10 ** DECIMALS, rounding);
• assets = shares.mulDiv(lastTotalAssets + 1, totalSupply() + 1, rounding);
