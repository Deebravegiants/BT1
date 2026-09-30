# [M] RedStone oracle is vulnerable be-

## Summary
Severity: Medium
Contest weight: 0.6911
Dataset id: 23132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Redstone oracle doesn't work as expected returning outdated or user selected prices leading to every asset using it return wrong ETH values. As we can see in the RedstoneOracle contract the actual ethUsdPrice and assetUsdPrice are state variables which need to be updated every time the getValueInEth function be called so to calculate the real value of the asset in ETH. We can see the implementation here :
```solidity
function getValueInEth(address, uint256 amt) external view returns (uint256) {
    if (priceTimestamp < block.timestamp - STALE_PRICE_THRESHOLD) revert RedstoneCoreOracle_StalePrice(ASSET);
    // scale amt to 18 decimals
    if (ASSET_DECIMALS <= 18) amt = amt * 10 ** (18 - ASSET_DECIMALS);
    else amt = amt / 10 ** (ASSET_DECIMALS - 18);
    // [ROUND] price is rounded down
    return amt.mulDiv(assetUsdPrice, ethUsdPrice);
}
```
However, the updatePrice function is not called from anywhere, not even from inside the getValueInEth function which should seem logical. Combined with the fact that the updatePrice function can be called by anyone ”giving” the price 3 minutes of liveness, the impact/result of this vulnerability is someone to take advantage of a price which is not updated and get a wrong value of the asset in ETH, either lower or higher than the real one. For example, he can borrow with the wrong price and repay with the right price which is a bit higher, so return less amount that he took. Here is the updatePrice of Redstone oracle :
```solidity
function updatePrice() external {
    // values[0] -> price of ASSET/USD
    // values[1] -> price of ETH/USD
    // values are scaled to 8 decimals
    uint256[] memory values = getOracleNumericValuesFromTxMsg(dataFeedIds);
    assetUsdPrice = values[0];
    ethUsdPrice = values[1];
    // RedstoneDefaultLibs.sol enforces that prices are not older than 3 mins.
    // since it is not
    // possible to retrieve timestamps for individual prices being passed, we consider the worst
    // case and assume both prices are 3 mins old
    priceTimestamp = block.timestamp - THREE_MINUTES;
}
```
Link to code

## Recommendation
Consider calling updatePrice in the getEthValue function :
```solidity
function getValueInEth(address, uint256 amt) external view returns (uint256) {
    updatePrice();
}
```
