# [M] M-04 | AutoCancel Validation May DoS Order Creation

## Summary
Severity: Medium
Contest weight: 0.0707
Dataset id: 21432
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MAX_TOTAL_CALLBACK_GAS_LIMIT_FOR_AUTO_CANCEL_ORDERS can change according to gas requirements of the system/chain. If this value decreases however, the position holders that already have maximum amount of callback gas used for their autoCancel orders can not call decrease order because the call will revert with MaxTotalCallbackGasLimitForAutoCancelOrdersExceeded.

## Recommendation
Before reducing this variable inform users about this problem and let them prepare their positions to handle with this case. Additionally, this validation does not need to take place for MarketDecrease orders.
