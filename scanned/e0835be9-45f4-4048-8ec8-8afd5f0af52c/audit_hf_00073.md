# [M] ORDA-2 | Markets With ETH As The shortToken Are Gameable

## Summary
Severity: Medium
Contest weight: 0.0668
Dataset id: 149
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event where a homogenous market or any GMX market had WETH as a short token, it would be possible for the user to withdraw their backing tokens through the refundWETH function, without going through the expected ACTION_WITHDRAW_FROM_ORDER cook action, therefore avoiding the solvency check and allowing for a user to cause their position to go insolvent.

## Recommendation
Such a market is unlikely to exist, however it should be explicitly stated that markets with Ether as the short token are incompatible with the system.
