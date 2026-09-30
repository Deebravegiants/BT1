# [H] Minting stake tokens is not updating the pool's

## Summary
Severity: High
Contest weight: 0.7624
Dataset id: 22873
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users mint new stake tokens, they provide liquidity to the pool, increasing the total amount and decreasing the borrowed utilization. However, this rate is not updated. When users mint stake tokens, they add liquidity to the pool and increase the total amount held in the pool:
```solidity
function _mintStakeToken(Mint.Request memory mintRequest) internal returns (uint256 stakeAmount) {
    //..
    pool.addBaseToken(cache.mintTokenAmount);
}
```
As we can see, the borrowing rate calculation will change accordingly. However, the rate is not updated:
```solidity
function getLongBorrowingRatePerSecond(LpPool.Props storage pool) external view returns (uint256) {
    if (pool.baseTokenBalance.amount == 0 && pool.baseTokenBalance.unsettledAmount == 0) {
        return 0;
    }
    int256 totalAmount = pool.baseTokenBalance.amount.toInt256() + pool.baseTokenBalance.unsettledAmount;
    if (totalAmount <= 0) {
        return 0;
    }
    uint256 holdRate = CalUtils.divToPrecision(
        pool.baseTokenBalance.holdAmount,
        totalAmount.toUint256(),
        CalUtils.SMALL_RATE_PRECISION
    );
    return CalUtils.mulSmallRate(holdRate, AppPoolConfig.getLpPoolConfig(pool.stakeToken).baseInterestRate);
}
```
Unfair accrual of borrowing fees. It can yield on lesser/higher fees for lps and position holders. It can also delay or cause unfair liquidations. Hence, high.

## Recommendation
Just like the opening orders update the rates after the pools base amounts changes.
