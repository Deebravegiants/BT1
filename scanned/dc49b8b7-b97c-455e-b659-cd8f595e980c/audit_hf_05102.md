# [M] Lack of slippage protection during withdrawal

## Summary
Severity: Medium
Contest weight: 0.5937
Dataset id: 23134
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Lack of slippage protection in the SuperPool and Pool could lead to loss of user funds in an event of bad debt liquidation.
When a user who has deposited assets in one of the pools of the Pool.sol contract wishes to withdraw them, they can do so by calling withdraw(). Under normal conditions, user expects to receive the full deposited amount back or more if the interest accrues in the underlying pool. However, if the pool experiences bad debt liquidation, the totalAssets of the pool are reduced by the amount of bad debt liquidated and the exchange rate worsens. Pool.sol#L542-L547
function withdraw(uint256 shares, address receiver, address owner) public returns (uint256 assets) {
    require(owner == msg.sender || isApprovedForAll[owner][msg.sender], "Pool: not approved");
    require(shares <= balanceOf[owner][poolId], "Pool: insufficient balance");

    // Accrue interest and fees
    (uint256 accruedInterest, uint256 feeShares) = simulateAccrue(pool);
    uint256 totalSupply = pool.totalDepositShares + feeShares;
    uint256 totalAssets = pool.totalDepositAssets + accruedInterest;

    // Convert shares to assets
    assets = _convertToAssets(shares, totalAssets, totalSupply, Math.Rounding.Down);
    
    // Rebalance bad debt across lenders
    pool.totalBorrowShares = totalBorrowShares - borrowShares;
    // handle borrowAssets being rounded up to be greater than totalBorrowAssets
    pool.totalBorrowAssets = (totalBorrowAssets > borrowAssets)
    ? totalBorrowAssets - borrowAssets
    : 0;
    uint256 totalDepositAssets = pool.totalDepositAssets;
    pool.totalDepositAssets = (totalDepositAssets > borrowAssets)
    ? totalDepositAssets - borrowAssets
    : 0;
}
```
When a user withdraws, if the pool experiences bad debt liquidation, while the transaction is pending in the mempool, they will burn more shares than they expected.
Consider the following scenario:
• pool.totalAssets = 2000.
• pool.totalShares = 2000.
• Bob wants to withdraw 500 assets, expecting to burn 500 shares.
• While Bob's transaction is pending in the mempool, the pool experiences a bad debt liquidation and totalAssets drops to 1500.
• When Bob's transaction goes through, he will burn 500*2000/1500=666.66 shares.
The same issue is present in the SuperPool contract, as the totalAssets() of the SuperPool is dependant on the total amount of assets in the underlying pools a SuperPool has deposited into.
```solidity
SuperPool.sol#L180-L189
function totalAssets() public view returns (uint256) {
    uint256 assets = ASSET.balanceOf(address(this));
    uint256 depositQueueLength = depositQueue.length;
    for (uint256 i; i < depositQueueLength; ++i) {
        assets += POOL.getAssetsOf(depositQueue[i], address(this));
    }
    return assets;
}
```
```solidity
Pool.sol#L218-L227
function getAssetsOf(
    uint256 poolId,
    address guy
) public view returns (uint256) {
    PoolData storage pool = poolDataFor[poolId];
    (uint256 accruedInterest, uint256 feeShares) = simulateAccrue(pool);
    return
        _convertToAssets(
            balanceOf[guy][poolId],
            pool.totalDepositAssets + accruedInterest,
            pool.totalDepositShares + feeShares,
            Math.Rounding.Down
        );
}
```
When redeeming in the SuperPool, a user will either burn more shares when using withdraw() or receive less assets when using redeem(). withdraw() in the Pool.sol and both redeem/withdraw in the SuperPool lack slippage protection, which can lead to users losing funds in the event of bad debt liquidation.

## Recommendation
Introduce minimum amount out for redeem() function and maximum shares in for withdraw() function as means for slippage protection.
