# [M] A manager benefits immediately when there

## Summary
Severity: Medium
Contest weight: 0.7014
Dataset id: 22922
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever users deposit tokens into the dHedge Pool, we take a snapshot of the current token price at the last fee mint point. The manager can profit from the increase in token price and the time passed since the last mint time. When users deposit tokens, the manager fee accumulated up to that point is credited to the manager. However, since the last mint token price is incorrectly recorded, the manager can immediately profit again, causing a reduction in token price within the same block. Imagine the total fund is F and the total share is S at this point. Then current token price is F/S. Now, imagine a user deposits tokens worth f into the dHedge Pool. During this deposit, the manager fee ms accumulated up to this point is credited to the manager.

```solidity
function _depositFor(
    address _recipient,
    address _asset,
    uint256 _amount,
    uint256 _cooldown
) private onlyAllowed(_recipient) whenNotFactoryPaused whenNotPaused returns (uint256 liquidityMinted) {
    require(IPoolManagerLogic(poolManagerLogic).isDepositAsset(_asset), "invalid deposit asset");
    ...
}
```

And the current price F/S is recorded as the last fee mint token price.

```solidity
function _mintManagerFee() internal returns (uint256 fundValue) {
    fundValue = IPoolManagerLogic(poolManagerLogic).totalFundValueMutable();
    uint256 tokenSupply = totalSupply();
    uint256 currentTokenPrice = _tokenPrice(fundValue, tokenSupply);
    if (tokenPriceAtLastFeeMint < currentTokenPrice) {
        tokenPriceAtLastFeeMint = currentTokenPrice;
    }
    lastFeeMintTime = block.timestamp;
}
```

Token price will be higher than F/S. If the new share for the depositor is s, then f/s > F/S due to the entry fee.

```solidity
function _depositFor(
    address _recipient,
    address _asset,
    uint256 _amount,
    uint256 _cooldown
) private onlyAllowed(_recipient) whenNotFactoryPaused whenNotPaused returns (uint256 liquidityMinted) {
    (, , uint256 entryFeeNumerator, uint256 denominator) = IPoolManagerLogic(poolManagerLogic).getFee();
    if (totalSupplyBefore > 0) {
        // Accounting for entry fee while calculating liquidity to be minted.
        liquidityMinted = usdAmount.mul(totalSupplyBefore).mul(denominator.sub(entryFeeNumerator)).div(fundValue).div(denominator);
    } else {
        // This is equivalent to doing liquidityMinted = liquidityMinted * (1 - entryFeeNumerator/denominator).
        liquidityMinted = usdAmount.mul(denominator.sub(entryFeeNumerator)).div(denominator);
    }
}
```

As a result, the current token price (F + f) / (S + s + ms) can be larger than F/S. This means if anyone calls the mintManagerFee function again in the same block, the additional manager fee is credited even though no time has passed since the last fee mint.

```solidity
function _availableManagerFee(
    uint256 _fundValue,
    uint256 _tokenSupply,
    uint256 _performanceFeeNumerator,
    uint256 _managerFeeNumerator,
    uint256 _feeDenominator
) internal view returns (uint256 available) {
    if (_tokenSupply == 0 || _fundValue == 0) return 0;
    uint256 currentTokenPrice = _fundValue.mul(10 ** 18).div(_tokenSupply);
    if (currentTokenPrice > tokenPriceAtLastFeeMint) {
        available = currentTokenPrice
            .sub(tokenPriceAtLastFeeMint)
            .mul(_tokenSupply)
            .mul(_performanceFeeNumerator)
            .div(_feeDenominator)
            .div(currentTokenPrice);
    }
}
```

This results in the depositor receiving shares at a token price (F + f) / (S + s + ms) that immediately drops within the same block. The log for the test is as below:

manager share before => 891000000000000  
manager share after => 9710464583763900

Please add below test to the test/unit/PoolLogicTest.ts:

```solidity
it("should account for entry fee when totalSupply is 0", async function () {
    const PoolManagerLogic = await ethers.getContractFactory("PoolManagerLogic");
    const poolManagerLogicAddr = await poolLogicProxy.poolManagerLogic();
    const poolManagerLogicProxy = PoolManagerLogic.attach(poolManagerLogicAddr);
    // refresh timestamp of Chainlink price round data
    await updateChainlinkAggregators(usdcPriceFeed, wethPriceFeed, linkPriceFeed);
    await assetHandler.setChainlinkTimeout(9000000);
    // Set the entry fee as 1.
    await poolManagerLogicProxy.connect(manager).announceFeeIncrease(10, 0, 100);
    await ethers.provider.send("evm_increaseTime", [3600 * 24 * 7 * 4]); // add 4 weeks
    await poolManagerLogicProxy.connect(manager).commitFeeIncrease();
    await poolLogicProxy.connect(investor).deposit(usdcProxy.address, (100e6).toString());
    await poolLogicProxy.connect(investor).deposit(usdcProxy.address, (1000e6).toString());
    console.log('manager share before => ', await poolLogicProxy.balanceOf(manager.address));
    await poolLogicProxy.mintManagerFee();
    console.log('manager share after => ', await poolLogicProxy.balanceOf(manager.address));
});
```

Of course, I agree that the manager can benefit from the token price increase. However, this immediate token price increase does not result from the manager's good strategy; it comes from the new deposits by this depositor. So the unfair aspect for the new depositor is that they may experience an immediate token price decrease within the same block. Therefore, the manager should not be able to profit from this.

## Recommendation
```solidity
function _depositFor(
    address _recipient,
    address _asset,
    uint256 _amount,
    uint256 _cooldown
) private onlyAllowed(_recipient) whenNotFactoryPaused whenNotPaused returns (uint256 liquidityMinted) {
    (, , uint256 entryFeeNumerator, uint256 denominator) = IPoolManagerLogic(poolManagerLogic).getFee();
    if (totalSupplyBefore > 0) {
        // Accounting for entry fee while calculating liquidity to be minted.
        liquidityMinted = usdAmount.mul(totalSupplyBefore).mul(denominator.sub(entryFeeNumerator)).div(fundValue).div(denominator);
    } else {
        // This is equivalent to doing liquidityMinted = liquidityMinted * (1 - entryFeeNumerator/denominator).
        liquidityMinted = usdAmount.mul(denominator.sub(entryFeeNumerator)).div(denominator);
    }
    uint256 fundValueAfter = fundValue.add(usdAmount);
    uint256 totalSupplyAfter = totalSupplyBefore.add(liquidityMinted);
    uint256 currentTokenPrice = _tokenPrice(fundValueAfter, totalSupplyAfter);
    if (tokenPriceAtLastFeeMint < currentTokenPrice) {
        tokenPriceAtLastFeeMint = currentTokenPrice;
    }
    lastFeeMintTime = block.timestamp;
}
```
