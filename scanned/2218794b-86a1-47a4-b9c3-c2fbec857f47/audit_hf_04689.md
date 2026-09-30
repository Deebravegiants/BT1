# [M] feeRecepient and insurance special addresses

## Summary
Severity: Medium
Contest weight: 0.4605
Dataset id: 22453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The protocol has 2 special addresses: feeRecepient and insurance, which receive fees from trading and liquidations. They receive their fees via Ciao.incrementFee function, which doesn't take debt into account. This means that if any of these accounts has debt in core collateral token for whatever reason, incrementFee will cause the account to have both asset balance and debt. If the balance is fully withdrawn, the core collateral asset is removed from the account and is no longer calculated in account health calculation. Such account might have core collateral debt which will be ignored and thus the account health calculations will be incorrect, allowing account to take more risk than it should, potentially causing bad debt and loss of funds for the other users.
The Ciao.incrementFee function simply increases recepient's asset balance without taking into account debt:
function incrementFee(
address asset,
uint256 fee,
address recipient
) external nonReentrant {
// check that the caller is the order dispatch or liquidation
_isBalanceUpdater();
subAccountAssets[recipient].add(asset);
_changeBalance(recipient, asset, int256(fee));
}
...
function _changeBalance(
address subAccount,
address asset,
int256 change
) internal {
int256 balanceBefore = int256(balances[subAccount][asset]);
if (change > 0) {
balances[subAccount][asset] += uint256(change);
} else {
balances[subAccount][asset] -= uint256(-change);
}
This function is called for feeRecepient and quote asset in OrderDispatch, and quote asset can be core collateral asset:
ciao.incrementFee(
product.quoteAsset,
uint256(takerFee + makerFee),
ciao.feeRecipient()
);
It is also called for insurance recepient for core collateral address in Liquidation:
ciao.incrementFee(
ciao.coreCollateralAddress(),
vars.liquidationFees,
ciao.insurance()
);
If either of these addresses has core collateral debt at the time of incrementFee call - it will not decrease debt, but will simply increase balance. When withdraw is called for this account with full amount, core collateral asset will be removed from the assets list:
function _withdraw(
address account,
address subAccount,
uint256 quantity,
address asset
) internal {
// The account has the full quantity withdrawn from balance
_changeBalance(subAccount, asset, -int256(quantity));
// if the balance becomes zero then remove the asset from the set
if (balances[subAccount][asset] == 0) {
subAccountAssets[subAccount].remove(asset);
}
...
This means account will have core collateral debt, but core collateral asset will be absent from the account's asset list. When calculating account health, it will ignore core collateral and will not count the debt:
tempVars.spotAssets = _ciao().getSubAccountAssets(subAccount);
tempVars.assetsLen = tempVars.spotAssets.length;
...
for (uint i = 0; i < tempVars.assetsLen; i++) {
address spotAssetAddress = tempVars.spotAssets[i];
uint32 spotProductId = _productCatalogue()
.baseAssetQuoteAssetSpotIds(
spotAssetAddress,
_ciao().coreCollateralAddress()
);
uint256 spotBalance = _ciao().balances(
subAccount,
spotAssetAddress
);
if (spotProductId == CORE_COLLATERAL_INDEX) {
health +=
int256(spotBalance) -
int256(_ciao().coreCollateralDebt(subAccount));
continue;
}
Since getSubAccountAssets won't return core collateral asset, core collateral balance - debt will never be added to health.
Incorrect account health calculation for specific accounts, allowing accounts to take on any debt which is not calculated in the account health, potentially creating bad debt and loss of funds for all protocol users.
```

## Recommendation
Check that incrementFee asset is core collateral, and settle core collateral balance instead of updating balance in such case.
