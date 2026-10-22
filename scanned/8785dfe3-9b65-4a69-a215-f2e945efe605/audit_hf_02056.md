# [M] Flashloan-Lowered StableBorrowRate For Mode-Switching Users

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 11688
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inherited from Aave, the Augmented Finance protocol supports both variable and stable borrow rates. The variable borrow rate follows closely the market dynamics and can be changed on each user interaction (either borrow, deposit, withdraw, repayment or liquidation). The stable borrow rate instead will be unaffected by these actions. However, implementing a fixed stable borrow rate model on top of a dynamic reserve pool is complicated and the protocol provides the rate-rebalancing support to work around dynamic changes in market conditions or increased cost of money within the pool. In the following, we show the code snippet of swapBorrowRateMode() which allows users to swap between stable and variable borrow rate modes. It follows the same sequence of convention by firstly validating the inputs (Step I), secondly updating relevant reserve states (Step II), then switching the requested borrow rates (Step III), next calculating the latest interest rates (Step IV), and finally performing external interactions, if any (Section V).
```solidity
function swapBorrowRateMode(address asset, uint256 rateMode)
    external
    override
    whenNotPaused
{
    DataTypes.ReserveData storage reserve = _reserves[asset];
    (uint256 stableDebt, uint256 variableDebt) = Helpers.getUserCurrentDebt(msg.sender, reserve);
    DataTypes.InterestRateMode interestRateMode = DataTypes.InterestRateMode(rateMode);
    ValidationLogic.validateSwapRateMode(
        reserve,
        _usersConfig[msg.sender],
        stableDebt,
        variableDebt,
        interestRateMode
    );
    reserve.updateState();
    if (interestRateMode == DataTypes.InterestRateMode.STABLE) {
        IStableDebtToken(reserve.stableDebtTokenAddress).burn(msg.sender, stableDebt);
        IVariableDebtToken(reserve.variableDebtTokenAddress).mint(
            msg.sender,
            msg.sender,
            stableDebt,
            reserve.variableBorrowIndex
        );
    } else {
        IVariableDebtToken(reserve.variableDebtTokenAddress).burn(
            msg.sender,
            variableDebt,
            reserve.variableBorrowIndex
        );
        IStableDebtToken(reserve.stableDebtTokenAddress).mint(
            msg.sender,
            msg.sender,
            variableDebt,
            reserve.currentStableBorrowRate
        );
    }
    reserve.updateInterestRates(asset, reserve.aTokenAddress, 0, 0);
    emit Swap(asset, msg.sender, rateMode);
}
```
Our analysis shows this swapBorrowRateMode() routine can be affected by a flashloan-assisted sandwiching attack such that the new stable borrow rate becomes the lowest possible. Note this attack is applicable when the borrow rate is switched from variable to stable rate. Specifically, to perform the attack, a malicious actor can first request a flashloan to deposit into the reserve pool so that the reserve's utilization rate is close to 0, then invoke swapBorrowRateMode() to perform the variable-to-borrow rate switch and enjoy the lowest currentStableBorrowRate (thanks to the nearly 0 utilization rate in current reserve), and finally withdraw to return the flashloan. A similar approach can also be applied to bypass maxStableLoanPercent enforcement in validateBorrow().

## Recommendation
Revise current execution logic of swapBorrowRateMode() to defensively detect sudden changes to a reserve utilization and block malicious attempts.
