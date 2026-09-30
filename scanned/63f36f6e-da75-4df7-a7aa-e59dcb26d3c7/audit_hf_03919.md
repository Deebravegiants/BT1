# [M] Shutting down a pool will prevent exits

## Summary
Severity: Medium
Contest weight: 0.5805
Dataset id: 20219
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The InfinityPool has the ability to shutdown. This ability is used to prevent deposits and borrows.
```solidity
/// @dev `isShuttingDown` is a boolean that, when true, halts deposits and borrows. Once set, it cannot be unset.
bool public isShuttingDown = false;
```
It is reasonable to shutdown the pool if it has a fundamental error (that an update will not sole) or to update. However - when the pool is shutting down also withdrawals/redeem from the ramp would be prevented. To withdraw from the SimpleRamp the staker calls the withdraw function.
```solidity
function withdraw(
    uint256 assets,
    address receiver,
    address owner,
    uint256
) public ownerIsCaller(owner) returns (uint256 shares) {
    shares = pool.convertToShares(assets);
    _processExit(owner, receiver, shares, assets);
}
```
_processExit will then be called
```solidity
function _processExit(
    address owner,
    address receiver,
    uint256 iFILToBurn,
    uint256 assetsToReceive
) internal {
    // if the pool can't process the entire exit, it reverts
    if (assetsToReceive > pool.getLiquidAssets())
        revert InsufficientLiquidity();
}
```
As can be seen above the code checks to see if the amount of assets to receive is larger then the pool liquidity of the pool. This is done by calling pool.getLiquidAssets()
```solidity
function getLiquidAssets() public view returns (uint256) {
    if(isShuttingDown) return 0;
}
```
If the pool is shutting down getLiquidAssets will return 0 and the transaction will revert. Users will not be able to withdraw their funds. If the pool will not update - their funds will be stuck in the pool.

## Recommendation
Consider removing the if(isShuttingDown) return 0 statement https://github.com/
