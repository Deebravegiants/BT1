# [H] DnGmxJuniorVaultManager#_rebalanceBor-

## Summary
Severity: High
Contest weight: 0.7894
Dataset id: 17776
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DnGmxJuniorVaultManager#_rebalanceBorrow fails to rebalance correctly if only one of the two assets needs a rebalance. In the case where one assets increases rapidly in price while the other stays constant, the vault may be liquidated.
```solidity
// If both eth and btc swap amounts are not beyond the threshold then no
// flashloan needs to be executed | case 1
if (btcAssetAmount == 0 && ethAssetAmount == 0) return;
if (repayDebtBtc && repayDebtEth) {
    // case where both the token assets are USDC
    // only one entry required which is combined asset amount for both tokens
    assets = new address[](1);
    amounts = new uint256[](1);
    assets[0] = address(state.usdc);
    amounts[0] = (btcAssetAmount + ethAssetAmount);
} else if (btcAssetAmount == 0 || ethAssetAmount == 0) {
    // Exactly one would be true since case-1 excluded (both false) | case-2
    // One token amount = 0 and other token amount > 0
    // only one entry required for the non-zero amount token
    assets = new address[](1);
    amounts = new uint256[](1);
    if (btcAssetAmount == 0) {
        assets[0] = (repayDebtBtc ? address(state.usdc) : address(state.wbtc));
        amounts[0] = btcAssetAmount;
    } else {
        assets[0] = (repayDebtEth ? address(state.usdc) : address(state.weth));
        amounts[0] = ethAssetAmount;
    }
```
The logic above is used to determine what assets to borrow using the flashloan. If the rebalance amount is under a threshold then the assetAmount is set equal to zero. The first check if(btcAssetAmount==0&&ethAssetAmount==0)return; is a short circuit that returns if neither asset is above the threshold. The third check elseif(btcAssetAmount==0||ethAssetAmount==0) is the point of interest. Since we short circuit if both are zero then to meet this condition exactly one asset needs to be rebalanced. The enter with the non-zero amount token but the actual logic reflects the opposite. If btcAssetAmount==0 it actually tries to enter with wBTC which would be the zero amount asset. The result of this can be catastrophic for the vault. If one token increases in value rapidly while the other is constant the vault will only ever try to rebalance the one token but because of this logical error it will never actually complete the rebalance. If the token increase in value enough the vault would actually end up becoming liquidated. Vault is unable to rebalance correctly if only one asset needs to be rebalanced, which can lead to the vault being liquidated

## Recommendation
Small change to reverse the logic and make it correct:
```solidity
if (btcAssetAmount != 0) {
    assets[0] = (repayDebtBtc ? address(state.usdc) : address(state.wbtc));
    amounts[0] = btcAssetAmount;
} else {
    assets[0] = (repayDebtEth ? address(state.usdc) : address(state.weth));
    amounts[0] = ethAssetAmount;
}
```
