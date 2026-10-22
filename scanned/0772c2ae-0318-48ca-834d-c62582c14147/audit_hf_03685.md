# [H] voltGNS#withdraw and redeem take fees from

## Summary
Severity: High
Contest weight: 0.1355
Dataset id: 19780
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC4626 vaults allow approved users to withdraw shares on behalf of another user. When this occurs fees are charged to msg.sender rather than the owner.
#L152-L162
sendWithdrawFees and sendRedeemFees transfers fees from msg.sender rather than the specified owner. This is problematic when a user withdraws/redeems on behalf of another user because they will be forced to pay the fees instead.
Wrong user pays fees when one users withdraws/redeems on behalf of the other

## Recommendation
sendWithdrawFees and sendRedeemFees should take shares from owner rather than msg.sender()
