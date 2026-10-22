# [H] DoS on refunds

## Summary
Severity: High
Contest weight: 0.7664
Dataset id: 6220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling claimRefundV2 if there is a reward claimable for certain beneficiary, it will enter the following if statement:
```solidity
if (claimer.isClaimable(_batchPayloadHash, _batchPayload, orderId, _beneficiary, maxReward, 1)) {
    escrowGMP.twoifyPayloadHash(orderId);
    ro.settlePayoutWithFeesCall(maxReward, rewardAsset, _beneficiary, address(ro), 1, orderId);
} else {
    emit NonRefundable(orderId, escrowGMP.getRemotePaymentPayloadHash(orderId), _batchPayloadHash);
}
```
After, if forwards the call to the settlePayoutWithFeesCall function inside the remote order contract where it tries to send funds via settleNativeOrToken:
```solidity
function settleNativeOrToken(
    uint256 amount,
    address asset,
    address beneficiary,
    address sender
) internal nonReentrant returns (bool) {
    if (amount == 0) return true;
    if (beneficiary == address(0)) return false;
    if (asset == address(0)) {
        (bool sent, ) = beneficiary.call{value: amount}("");
        return sent;
    }
    IERC20(asset).safeTransferFrom(sender, beneficiary, amount);
    return true;
}
```
Notice both of the key parameters, sender and beneficiary. According to the first call in the claimRefundV2 functions, the sender was specified to be the remote order contract address(ro), which in this case it does act like address(this). safeTransferFrom requires a pre-approval for the funds to be transferred and when calling it from the same contract it will revert.

## Recommendation
If the sender address is meant to be address(this) (the remote order contract) use safeTransfer instead than safeTransferFrom.
