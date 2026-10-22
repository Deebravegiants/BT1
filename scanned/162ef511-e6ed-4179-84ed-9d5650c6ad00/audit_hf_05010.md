# [M] SMR price will be used for more period than maxStalePeriod

## Summary
Severity: Medium
Contest weight: 0.4541
Dataset id: 22999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function getPrice(address asset) external view override returns (uint256) {
    uint256 decimals;
    if (asset == SMR_ADDR) {
        decimals = 18;
        asset = WSMR;
    } else {
        IERC20Metadata token = IERC20Metadata(asset);
        decimals = token.decimals();
    }
    if (tokenConfigs[asset].asset == address(0)) revert("asset not exist");
    uint256 price = prices[asset];
    // if price is 0, it means the price hasn't been updated yet and it's meaningless, revert
    if (price == 0) revert("TWAP price must be positive");
    uint256 maxStalePeriod = tokenConfigs[asset].maxStalePeriod;
    // revert when last price update plus max stale period passed
    if (block.timestamp > blockTimestampLast[asset] + maxStalePeriod)
        revert("stale price");
    return (price * (10 ** (18 - decimals)));
}
```
SMR price will be used for more period than maxStalePeriod. If a token price is from SMR based pool. In order to calculate the price of the token TwapOracle contract first fetches the price of the token in SMR and then converts that price into USDC using smrPrice which is fetched from SMR/USDC pool. Let's say I want the price of TRX token. But the DEX doesn't contain a pool for TRX/USDC. It only has a pool for TRX/SMR. So first I will read the price of TRX in SMR from TRX/SMR pool and then convert it to USDC using SMR price read from SMR/USDC pool. Let's say that the maxStalePeriod of SMR is 2 hours. and maxStalePeriod of TRX is also 2 hours. If price of TRX is calculated when SMR price is already 1.9 hours old. That newly calculated price will marked as fresh for the next 2 hours and used for next 2 hours. But as the SMR price is already 1.9 hours which is used for TRX price calculation. In this case it will be used for additional 2 more hours. leading to consumption of price for more than maxStalePeriod. SMR price will be consumed for more than maxStalePeriod.

## Recommendation
No recommendation available
