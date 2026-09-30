# [H] The manager can steal the rewards from all

## Summary
Severity: High
Contest weight: 0.9030
Dataset id: 22937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a Vault deposits liquidity into a Velodrome Concentrated Liquidity Pool (CLPool), it also has the option to stake that liquidity into a Velodrome Gauge, which will give rewards in the VELO token. However, the manager can directly call getReward while the VELO token is not supported in the Vault to steal those rewards from the Vault's users. Whenever the Vault has some liquidity staked into a Velodrome Gauge, the rewards generated from that staking are accounted towards the total Vault's value, which is accounted in VelodromeCLAssetGuard: s/guards/assetGuards/velodrome/VelodromeCLAssetGuard.sol#L129-L134
```solidity
if (isStaked) {
    //during increasing/decreasing staked liquidity the rewards move from earned to rewards
    address rewardToken = clGauge.rewardToken();
    tokenBalance = tokenBalance.add(_assetValue(pool, rewardToken, clGauge.earned(pool, tokenId)));
    tokenBalance = tokenBalance.add(_assetValue(pool, rewardToken, clGauge.rewards(tokenId)));
}
```
These rewards are accounted towards the total Vault's value even if the VELO token is supported or not. However, the manager uses the Vault to call CLGauge::getReward while the VELO token is not supported so those tokens are transferred to the Vault but are not accounted for the total value because that token is not supported. The function totalFundValueMutable, which is in charge of getting the total Vaul'ts value, will only loop over the supported assets:
```solidity
function totalFundValueMutable() external override returns (uint256 total) {
    uint256 assetCount = supportedAssets.length;
    for (uint256 i; i < assetCount; ++i) {
        address asset = supportedAssets[i].asset;
        address guard = IHasGuardInfo(factory).getAssetGuard(asset);
        uint256 balance;
        (bool hasFunction, bytes memory answer) = guard.call(abi.encodeWithSignature("isStateMutatingGuard()"));
        if (hasFunction && abi.decode(answer, (bool))) {
            balance = IMutableBalanceAssetGuard(guard).getBalanceMutable(poolLogic, asset);
        } else {
            balance = IAssetGuard(guard).getBalance(poolLogic, asset);
        }
        total = total.add(assetValue(asset, balance));
    }
}
```
Because of this, the unclaimed rewards from a Velodrome Gauge will be counted towards the Vault's total value, but if the manager disables the VELO token and claims the rewards, those tokens will be removed from the total value. This means that the users will experience a drop in the Vault's share price because the rewards are removed from the total assets. After the rewards are maliciously claimed by the manager, he could steal most of them by swapping the VELO tokens on 1Inch allowing 100% slippage, and sandwiching that transaction to extract the value. Usually, if a manager wants the Vault to perform a swap using 1Inch, some checks ensure that the slippage cannot be high to protect the user's funds. This is checked at SlippageAccumulator::updateSlippageImpact: s/utils/SlippageAccumulator.sol#L89
```solidity
function updateSlippageImpact(SwapData calldata swapData) external onlyContractGuard(swapData.to) {
    if (IHasSupportedAsset(swapData.poolManagerLogic).isSupportedAsset(swapData.srcAsset)) {
    }
}
```
However, as the code snippet is showing, the slippage of a swap won't be checked if the token being swapped is not supported by the Vault. Using this, a manager can trade all the untracked VELO allowing all the slippage, and can sandwich that transaction by extracting the maximum value out of that swap. will call _getReward internally. The manager can steal all VELO rewards from all Velodrome Gauges.

## Recommendation
To mitigate this issue is recommended to check if the reward token is supported by the Vault before letting the manager call the functions getReward and withdraw.
```solidity
} else if (method == IVelodromeCLGauge.withdraw.selector) {
    uint256 tokenId = abi.decode(params, (uint256));
    _validateTokenId(nonfungiblePositionManagerGuard, tokenId, poolLogic);
    address rewardToken = velodromeCLGauge.rewardToken();
    require(IHasSupportedAsset(poolManagerLogic).isSupportedAsset(rewardToken), "unsupported asset: rewardToken");
    txType = uint16(TransactionType.VelodromeCLUnstake);
} else if (method == bytes4(keccak256("getReward(uint256)"))) {
    // it's possible to claim any reward token and sell it, we don't check if the reward token is supported
    uint256 tokenId = abi.decode(params, (uint256));
    _validateTokenId(nonfungiblePositionManagerGuard, tokenId, poolLogic);
    address rewardToken = velodromeCLGauge.rewardToken();
    require(IHasSupportedAsset(poolManagerLogic).isSupportedAsset(rewardToken), "unsupported asset: rewardToken");
    txType = uint16(TransactionType.Claim);
}
return (txType, false);
```
