# [M] Non-VIP Withdraw Fee Bypass with JIT VIP Status

## Summary
Severity: Medium
Contest weight: 0.4309
Dataset id: 13184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Tender.fi protocol provides incentive mechanisms that oﬀer diﬀerent fees based on the holding amount of TND balance. While examining the current logic in computing the associated fee, we notice the so-called non-VIP fee charge may be bypassed. To elaborate, we show below the related code snippet to determine the membership-related fee factors. It comes to our attention the holding TND balance is queried from the tndAddress token, which allows a window opportunity to have a just-in-time (JIT) balance for VIP membership beneﬁts. In particular, a protocol user may ﬂashloan the required balance (tokenBalanceVipThreshold) right before the withdraw operation and return the same amount immediately after the operation. By doing so, the user can simply enjoy the membership beneﬁts without actual cost!

```solidity
function getIsAccountVip(address _account) public view override returns (bool) {
    if (vipNft != address(0)) {
        if (IERC721(vipNft).balanceOf(_account) > 0) {
            return true;
        }
    }
    if (whitelistedUser[_account]) {
        return true;
    }
    if (compAddress != address(0) && tokenBalanceVipThreshold > 0) {
        if (EIP20Interface(compAddress).balanceOf(_account) >= tokenBalanceVipThreshold ||
            EIP20Interface(tndAddress).balanceOf(_account) >= tokenBalanceVipThreshold) {
            return true;
        }
    }
    return false;
}
```

## Recommendation
Revisit the membership fee design to ensure it cannot be bypassed. Note other operations (e.g., redeem and borrow) share the same issue.
