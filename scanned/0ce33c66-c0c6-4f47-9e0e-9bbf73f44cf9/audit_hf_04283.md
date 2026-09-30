# [C] C-02 | AutoCancellation Prevents Liquidations

## Summary
Severity: Critical
Contest weight: 0.2907
Dataset id: 21422
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation OrderUtils.executeOrder will be called. This function will check if this is a decrease order and if sizeInUsd is 0 after the order execution, if so will call clearAutoCancelOrders. Indeed liquidation order is a decrease order and sizeInUsd after liquidation will be 0, hence AutoCancellation mechanism will always be triggered with liquidations. AutoCancellation will check for all stop-loss/take-profit orders available for that position which can be as high as 10 in current configuration. This cancellation can do possibly 10 callback calls with sending 2.000.000 gas for each. Additionally, for every cancellation the gas usage is around 600.000. When we also considered the fee refund mechanism's callback call which per call will send 500.000 gas, we can possibly reach total amount of 31.000.000 and more when considering liquidation's gas usage itself. So a liquidation order might require more than 31.000.000 gas which is more than block gas limit in avalanche and also can be possibly problematic in Arbitrum because it is expected from keepers to provide this amount of gas while it is not ensured the keeper provided sufficient amount of gas for all these actions.

## Recommendation
Multiple steps are required to resolve the issue in its entirety:
1. Either decrease the max auto cancel amount or further restrict gas usage for cancellation callback. Combination of both can also be used. In the end, it is crucial to check maximum possible gas usage for AutoCancellation related actions.
2. Include auto cancellation's gas usage when checking keeper's provided gas amount especially when it is a liquidation order.
