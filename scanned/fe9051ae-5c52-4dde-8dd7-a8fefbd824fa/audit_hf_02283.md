# [M] Potential Denial-of-Service in Token Graduation

## Summary
Severity: Medium
Contest weight: 0.4509
Dataset id: 12492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, MaxFun builds an innovative DeFi platform that caters to the launch, liquidity management, and automated market operations of new tokens. When a new token is launched, it Public will go through the so-called graduation process. Our analysis shows the token graduation may suffer from a denial-of-service issue. In the following, we show the implementation of the related launchOnUniswap() routine. When the new token launch process reaches the target launchPointShare, this routine will be invoked. As part of its logic, it will call the swapFactory contract to create the token pair and add the initial liquidity. However, the token pair creation may be blocked (line 162) if the external pair is already created, resulting in the token graduation failure.
```solidity
function launchOnUniswap(address tokenAddress, address asset) public onlyFactory returns (address) {
    address pairAddress = IMaxFunCurve(maxFunCurve).getPair(tokenAddress, asset);
    IMaxFunPair pair = IMaxFunPair(pairAddress);
    uint256 assetBalance = pair.assetBalance();
    IMaxFunCurve(maxFunCurve).triggerGraduation(tokenAddress, asset);
    address uniswapV2Pair = _createUniswapV2Pool(tokenAddress, asset);
    uint256 txFee = (maxFunFactory.getGradFee() * assetBalance) / maxFunFactory.getPercentageDecimals();
    IERC20(asset).safeTransfer(maxFunFactory.getTaxVault(), txFee);
    _addInitialLiquidity(tokenAddress, asset);
    emit Graduated(tokenAddress, uniswapV2Pair);
    return uniswapV2Pair;
}

function _createUniswapV2Pool(address tokenAddress, address asset) internal returns (address uniswapV2Pair_) {
    uniswapV2Pair_ = IUniswapV2Factory(swapFactory).createPair(tokenAddress, asset);
    _liquidityPools.add(uniswapV2Pair_);
    emit UniswapV2PairCreated(uniswapV2Pair_);
    return uniswapV2Pair_;
}
```

## Recommendation
Revise the above routine to ensure the token graduation is not blocked.
