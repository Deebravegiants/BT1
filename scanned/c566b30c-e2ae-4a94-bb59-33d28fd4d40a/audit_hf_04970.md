# [M] VelodromeCLPriceLibrary::assertFairPrice()

## Summary
Severity: Medium
Contest weight: 0.4619
Dataset id: 22930
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the deviation threshold of the oracle of an asset in a Velodrome NFT position is greater than 0.3% all withdrawals could be halted and the manager prevented from increasing liquidity or minting a new NFT positions. The function VelodromeCLPriceLibrary::assertFairPrice() is responsible for ensuring that a Velodrome pool current pricing is within an acceptable range. The range is defined as a maximum difference of 0.3% (or 50% more than the pool fee if the fee is higher than 0.3%) between the pool "fair price" (ie. the price the pool tokens should have relative to each other based on external oracles) and the "actual price" (ie. the price the pool tokens actually have relative to each other based on the current reserves of the pool):

```solidity
function assertFairPrice(address dhedgeFactory, address velodromeCLPool, uint24 fee) internal view returns (uint160 sqrtPriceX96) {
    IVelodromeCLPool uniPool = IVelodromeCLPool(velodromeCLPool);
    (sqrtPriceX96, , , , , ) = uniPool.slot0();
    // Get a fair sqrtPriceX96 from asset price oracles
    // We pass the tokens in the same order as the pool is configured
    uint160 fairSqrtPriceX96 = getFairSqrtPriceX96(dhedgeFactory, uniPool.token0(), uniPool.token1());
    // Check that fair price is close to current pool price
    // Threshold for the check is:
    // - minimum of 0.3%, and
    // - 50% higher than pool fee, because the pool may not get arbed if the fee is high
    uint256 threshold = fee >= MIN_THRESHOLD ? fee.mul(150).div(100) : MIN_THRESHOLD;
    require(
        sqrtPriceX96 < fairSqrtPriceX96.add(fairSqrtPriceX96.mul(threshold).div(1_000_000)) &&
        fairSqrtPriceX96 < sqrtPriceX96.add(fairSqrtPriceX96.mul(threshold).div(1_000_000)),
        "Velodrome CL price mismatch"
    );
}
```

The function reverts whenever the sqrtPriceX96 (ie. actual pool price) is not within the 0.3% range relative to the fairSqrtPriceX96 (ie. price the pool "should" have based on oracle pricing). This can be problematic if the oracle used to determine the fairSqrtPriceX96 have a "deviation threshold" greater than 0.3%. If, as an example, the assets in the Velodrome pool use oracles with a "deviation threshold" of 0.5% the price might not get updated until the price change is at least 0.5%, this could result in VelodromeCLPriceLibrary::assertFairPrice() reverting because the difference between fairSqrtPriceX96 and sqrtPriceX96 is bigger than 0.3%. VelodromeCLPriceLibrary::assertFairPrice() is used in multiple part of the codebase to ensure the Velodrome pool interacting with the protocol is not imbalanced: • VelodromeNonfungiblePositionGuard::txGuard(): when increasing liquidity or minting a new NFT position • VelodromeCLGaugeContractGuard::txGuard(): when increasing liquidity • VelodromeCLAssetGuard::getBalance(): used in PoolLogic::_withdrawProcessing() whenever a withdrawal is executed In particular PoolLogic::_withdrawProcessing() is executed on each withdrawal and if VelodromeCLPriceLibrary::assertFairPrice() reverts all of the withdrawals reverts. One asset that has a 0.5% deviation threshold is VELO/USD. When the deviation threshold of the oracle of an asset in a Velodrome NFT position is greater than 0.3% all withdrawals could be halted and the manager prevented from increasing liquidity or minting a new position.

## Recommendation
Increase the threshold check in VelodromeCLPriceLibrary::assertFairPrice() to the maximum used by the used oracles. This should be 0.5% but I might have missed some assets with a higher threshold.
