# [M] `YieldStakingBase.stake`

## Summary
Severity: Medium
Contest weight: 0.7063
Dataset id: 22319
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Code reference: [YieldLogic.sol#L150](https://github.com/code-423n4/2024-12-benddao/blob/489f8dd0f8e86e5a7550cc6b81f9edfe79efbf4e/src/libraries/logic/YieldLogic.sol#L150)

In [this PR](https://github.com/BendDAO/bend-v2/pull/10), `yieldSetERC721TokenData()` adds the following restrictions:
```solidity
function executeYieldSetERC721TokenData(InputTypes.ExecuteYieldSetERC721TokenDataParams memory params) internal {
    ...
    if (params.isLock) {
        require(ymData.yieldCap > 0, Errors.YIELD_EXCEED_STAKER_CAP_LIMIT);

        require(tokenData.lockerAddr == address(0), Errors.ASSET_ALREADY_LOCKED_IN_USE);

        VaultLogic.erc721SetTokenLockerAddr(nftAssetData, params.tokenId, lockerAddr);
    } else {
        require(tokenData.lockerAddr == lockerAddr, Errors.YIELD_TOKEN_LOCKED_BY_OTHER);

        VaultLogic.erc721SetTokenLockerAddr(nftAssetData, params.tokenId, address(0));
    }
```
This causes `yieldSetERC721TokenData()` to be called only once. This is fine for `YieldWUSDStaking.sol`. But for the other `YieldStakingBase.sol`, there is a problem, because it is not possible to increase borrowing again (Health Factor is still enough) as before.

In `YieldStakingBase.stake()`
```solidity
function _stake(uint32 poolId, address nft, uint256 tokenId, uint256 borrowAmount) internal virtual {
    ...
    YieldStakeData storage sd = stakeDatas[nft][tokenId];
    if (sd.yieldAccount == address(0)) {
        require(vars.nftLockerAddr == address(0), Errors.YIELD_ETH_NFT_ALREADY_USED);

        vars.totalDebtAmount = borrowAmount;

        sd.yieldAccount = address(vars.yieldAccout);
        sd.poolId = poolId;
        sd.state = Constants.YIELD_STATUS_ACTIVE;
    } else {
        require(vars.nftLockerAddr == address(this), Errors.YIELD_ETH_NFT_NOT_USED_BY_ME);
        require(sd.state == Constants.YIELD_STATUS_ACTIVE, Errors.YIELD_ETH_STATUS_NOT_ACTIVE);
        require(sd.poolId == poolId, Errors.YIELD_ETH_POOL_NOT_SAME);

        vars.totalDebtAmount = convertToDebtAssets(poolId, sd.debtShare) + borrowAmount;
    }
    ....
    poolYield.yieldSetERC721TokenData(poolId, nft, tokenId, true, address(underlyingAsset));

    // check hf
    uint256 hf = calculateHealthFactor(nft, nc, sd);
    require(hf >= nc.unstakeHeathFactor, Errors.YIELD_ETH_HEATH_FACTOR_TOO_LOW);

    emit Stake(msg.sender, nft, tokenId, borrowAmount);
}
```

## Recommendation
Two possible modifications

1. `_stake()` does not call `poolYield.yieldSetERC721TokenData()` if appending.
```solidity
function _stake(uint32 poolId, address nft, uint256 tokenId, uint256 borrowAmount) internal virtual {
    ...
    require(vars.nftLockerAddr == address(this), Errors.YIELD_ETH_NFT_NOT_USED_BY_ME);
    require(sd.state == Constants.YIELD_STATUS_ACTIVE, Errors.YIELD_ETH_STATUS_NOT_ACTIVE);
    require(sd.poolId == poolId, Errors.YIELD_ETH_POOL_NOT_SAME);

    vars.totalDebtAmount = convertToDebtAssets(poolId, sd.debtShare) + borrowAmount;
}
....
// poolYield.yieldSetERC721TokenData(poolId, nft, tokenId, true, address(underlyingAsset));
}
```

2. `yieldSetERC721TokenData()` to allow the current `nftLockerAddr` to execute.
```diff
function executeYieldSetERC721TokenData(InputTypes.ExecuteYieldSetERC721TokenDataParams memory params) internal {
    ...
    if (params.isLock) {
        require(ymData.yieldCap > 0, Errors.YIELD_EXCEED_STAKER_CAP_LIMIT);

-       require(tokenData.lockerAddr == address(0), Errors.ASSET_ALREADY_LOCKED_IN_USE);
+       require(tokenData.lockerAddr == address(0) || tokenData.lockerAddr == lockerAddr), Errors.ASSET_ALREADY_LOCKED_IN_USE);

        VaultLogic.erc721SetTokenLockerAddr(nftAssetData, params.tokenId, lockerAddr);
    } else {
        require(tokenData.lockerAddr == lockerAddr, Errors.YIELD_TOKEN_LOCKED_BY_OTHER);

        VaultLogic.erc721SetTokenLockerAddr(nftAssetData, params.tokenId, address(0));
    }
```
It is recommended to choose option (2).

Fixed in [commit eef87bf](https://github.com/BendDAO/bend-v2/commit/eef87bf78207810a2404375ef352cc8282cc3162)
