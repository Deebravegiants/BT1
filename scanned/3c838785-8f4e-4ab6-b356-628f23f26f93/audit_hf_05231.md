# [H] Insufficient duration validation in STBL_Register::setupAsset can lock user withdrawals

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23389
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lackof duration validation in STBL_Register::setupAsset and STBL_Register::setDurations allows asset configurations where `yieldDuration > duration`, creating mathematically impossible withdrawal conditions that lock user funds.

The withdrawal logic requires users to wait at least `yieldDuration` while also withdrawing before `duration` expires. When `yieldDuration > duration`, no valid time window exists for user withdrawals.

The `iWithdraw` function in `STBL_LT1_Issuer` has the following checks:

```solidity
function iWithdraw(uint256 _tokenID, address _sender) internal isSetupDone {
    YLD_Metadata memory MetaData = iSTBL_YLD(registry.fetchYLDToken()).getNFTData(_tokenID);
    // code..
    //ensures that users can't withdraw after duration has passed
    if ((MetaData.depositBlock + MetaData.Fees.duration) < block.timestamp)
        revert STBL_Asset_WithdrawDurationNotReached(assetID, _tokenID);
    //ensures that users must wait for yield duration to withdraw assets
    if (
        (MetaData.depositBlock + MetaData.Fees.yieldDuration) >
        block.timestamp
    ) revert STBL_Asset_YieldDurationNotReached(assetID, _tokenID);
    // @audit withdrawal proceeds only if BOTH conditions are false...
    //@audit when yieldDuration > duration, no withdrawal window exists for users
}
```

Impact: Incorrectly configured asset durations can prevent user withdrawals.

## Recommendation
Consider adding duration relationship validation in `setupAsset` and `setDurations`.
