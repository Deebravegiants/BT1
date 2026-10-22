# [M] ETH transfer griefing

## Summary
Severity: Medium
Contest weight: 0.4096
Dataset id: 8205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
forceCancelOrder() uses a direct address call to send ETH to buyer and seller on refund in ETH.

```solidity
if (offer.exToken == address(0)) {
    // refund ETH
    if (buyerRefundValue > 0 && buyer != address(0)) {
        (bool success,) = buyer.call{value: buyerRefundValue}('');
        require(success, 'Transfer Funds to Seller Fail');
    }
    if (sellerRefundValue > 0 && seller != address(0)) {
        (bool success,) = seller.call{value: sellerRefundValue}('');
        require(success, 'Transfer Funds to Seller Fail');
    }
}
```

Both buyer and seller can grief each other reverting on these calls, blocking refund execution for both parties and managing the suitable time/conditions to finalize the refund. In the worst cases, it can be used as a means of blackmailing. In addition, it can be not intentional reverts, e.g. when the receiver is a smart-contract that hasn't designed refund logic (and cannot receive ETH).

## Recommendation
Consider implementing a claiming logic when users do not receive calls and transfers, and the contract stores their pending withdrawals. Users have to use a separate function to claim these funds. This logic is worth implementing for all ETH transfers - including settleFilled(), settle2Steps() and cancelOffer().
