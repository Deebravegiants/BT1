# [M] LendingPool::setBorrowingRate

## Summary
Severity: Medium
Contest weight: 0.4640
Dataset id: 1886
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The missing calls to updateState and updateInterestRates from LendingPool::setBorrowingRateConfig will result to the update to not having an immediate effect on the currentBorrowingRate and instead waiting for the next action to update it.
In LendingPool::setBorrowingRateConfig, the code is trying to update the current configuration for the borrowingRates depending on the utilisationRate of the reserve.
Let's see the implementation of the function :
```solidity
function setBorrowingRateConfig(
    DataTypes.ReserveData storage reserve,
    uint16 utilizationA,
    uint16 borrowingRateA,
    uint16 utilizationB,
    uint16 borrowingRateB,
    uint16 maxBorrowingRate
) internal {
    // (0%, 0%) -> (utilizationA, borrowingRateA) -> (utilizationB, borrowingRateB) -> (100%, maxBorrowingRate)
    reserve.borrowingRateConfig.utilizationA = uint128(
        Precision.FACTOR1E18.mul(utilizationA).div(Constants.PERCENT_100)
    );
    reserve.borrowingRateConfig.borrowingRateA = uint128(
        Precision.FACTOR1E18.mul(borrowingRateA).div(Constants.PERCENT_100)
    );
    reserve.borrowingRateConfig.utilizationB = uint128(
        Precision.FACTOR1E18.mul(utilizationB).div(Constants.PERCENT_100)
    );
    reserve.borrowingRateConfig.borrowingRateB = uint128(
        Precision.FACTOR1E18.mul(borrowingRateB).div(Constants.PERCENT_100)
    );
    reserve.borrowingRateConfig.maxBorrowingRate = uint128(
        Precision.FACTOR1E18.mul(maxBorrowingRate).div(
            Constants.PERCENT_100
        )
    );
}
```
Link to code
As we can see, this pretty much means that before the call of this function the current utilisationRate and the corresponding currentBorrowingRate but after the call of this function the current utilisationRate to give different borrowingRate. However, this function fails to updateState and updateInterestRates meaning that the new borrowingRate that the protocol wants to have for the current utilisationRate is indefinite when it will be set and for the period between now until the next action that will update the state, the old borrowingRate will be used.
Internal pre-conditions
N/A
External pre-conditions
N/A
Attack Path
1. Reserve is deployed with a specific borrowingRateConfig
2. After some time, protocol wants to update this borrowingRateConfig and calls LendingPool::setBorrowingRateConfig.
3. However, this new borrowingRateConfig will not be actually used until an action on the LendingPool being performed.
The impact of this vulnerability is that the protocol will actually have not control of when the new borrowingRateConfig will be actually activated. For the meantime between the setBorrowingConfigRate until the next action on the LendingPool which will update the interest rates (which is **indefinite**), the currentBorrowingRate that will be used will be the old one which was based on the previous borrowingRateConfig. This means that the protocol can lose funds since they will want for example for the current utilization rate to have 25% interest rate but instead they will have the previous 15% interest rate until someone update the state by deposit/borrow...

## Recommendation
Consider calling updateState before the change of the configuration and updateInterestRates after the change of the configuration during the LendingPool::setBorrowingRateConfig call, in order to the update of the configuration to have instant and immediate effect on the reserve.currentBorrowingRate.
