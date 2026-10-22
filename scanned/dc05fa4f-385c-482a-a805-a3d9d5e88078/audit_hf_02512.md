# [M] Inaccurate Tip Bucket Balance Calculation in VolatilePool

## Summary
Severity: Medium
Contest weight: 0.4053
Dataset id: 13410
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the VolatilePool support allows for eﬃcient re-pegging, which by design allocates certain reserve from the accumulated fee. The reserve fee is saved in the pool. However, this reserve fee is not excluded from the tip bucket balance calculation. To elaborate, we show below the code snippet from the tipBucketBalance() routine. This routine has a rather straightforward logic in deducting the cash amount (line 667) and collected fee (line 668) from the current balance. Notice the reserve fee is also part of the current balance. With that, there is a need to deduct the repeg-related reserve fee as well.
```solidity
function tipBucketBalance(PoolV4Data storage poolData, IERC20 token) external view returns (uint256 balance) {
    IAsset asset = poolData.assets.assetOf(token);
    return asset.underlyingTokenBalance().toWad(asset.underlyingTokenDecimals())
        - asset.cash()
        - poolData.feeAndReserve[asset].feeCollected;
}
```

## Recommendation
Revisit the above logic to compute the intended tip bucket balance.
