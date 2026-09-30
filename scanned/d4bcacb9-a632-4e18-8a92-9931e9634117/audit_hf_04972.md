# [M] VelodromeCLPriceLibrary::calculateSqrtPrice()

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 22932
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function VelodromeCLPriceLibrary::calculateSqrtPrice() can revert in some situations preventing users from redeeming their shares. The function VelodromeCLPriceLibrary::calculateSqrtPrice() is used to get the square root price of a Velodrome pool given prices returned by oracles:
```solidity
function calculateSqrtPrice(
    uint256 token0Price,
    uint256 token1Price,
    uint8 token0Decimals,
    uint8 token1Decimals
) internal pure returns (uint160 sqrtPriceX96) {
    uint256 priceRatio = token0Price.mul(10 ** token1Decimals).div(token1Price);
    // Overflow protection for the price ratio shift left
    bool overflowProtection;
    if (priceRatio > 10 ** 18) {
        overflowProtection = true;
        priceRatio = priceRatio.div(10 ** 10); // decrease 10 decimals
    }
    require(priceRatio <= 10 ** 18 && priceRatio > 1000, "VeloCL price ratio out of bounds");
    sqrtPriceX96 = uint160(DhedgeMath.sqrt((priceRatio << 192).div(10 ** token0Decimals)));
    if (overflowProtection) {
        sqrtPriceX96 = uint160(sqrtPriceX96.mul(10 ** 5)); // increase 5 decimals (revert adjustment)
    }
}
```
The function reverts if the calculated priceRatio is greater than 1e18 or lower than 1000. Given the assets accepted by Dhedge this requirement might cause reverts in situations where reverts should not happen. Let's take as example the pair of assets VELO and WBTC:
• VELO: token0Price =~ 1e16, token0Decimals = 18
• WBTC: token1Price =~ 64000e18, token1Decimals = 8
With these parameters, the priceRatio will result in:
priceRatio = (token0Price × 10^token1Decimals)/token1Price = (1e16 × 1e8)/64000e18 ≈ 15.62
which would make the function revert because the result is lower than 1000. There are more possible examples given the protocol accepts VelodromeV2 LPs as assets as well, which have a price lower than VELO: the price returned by the Velodrome STABLE_USDC_DAI oracle is 199995051485545 =~ 1e14. The function VelodromeCLPriceLibrary::calculateSqrtPrice() is used by VelodromeCLPriceLibrary::assertFairPrice(), which is used by VelodromeCLAssetGuard::getBalance(), which is used during the withdrawal process. As a consequence VelodromeCLPriceLibrary::calculateSqrtPrice() reverting would prevent anybody from withdrawing. It's possible for an NFT position to be minted by the manager/trader and enter a state in which VelodromeCLPriceLibrary::calculateSqrtPrice() reverts only after some time.

## Recommendation
I'm not sure why and how the 1000 and 1e18 boundaries were established, but consider changing it or removing it.
