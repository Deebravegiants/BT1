# [M] `withdraw` should allow taking out borrowed assets regardless of collateral ratio

## Summary
Severity: Medium
Contest weight: 0.5910
Dataset id: 21550
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
We can withdraw `underlyingCollateralToken` and `underlyingBorrowToken` by `withdraw()`:
    
    ```solidity
    function withdraw(WithdrawParams calldata params) external payable override(ISize) whenNotPaused {
        state.validateWithdraw(params);
        state.executeWithdraw(params);
        state.validateUserIsNotBelowOpeningLimitBorrowCR(msg.sender);
    }

    function executeWithdraw(State storage state, WithdrawParams calldata params) public {
        uint256 amount;
        if (params.token == address(state.data.underlyingBorrowToken)) {
            amount = Math.min(params.amount, state.data.borrowAToken.balanceOf(msg.sender));
            if (amount > 0) {
                state.withdrawUnderlyingTokenFromVariablePool(msg.sender, params.to, amount);
            }
        } else {
            amount = Math.min(params.amount, state.data.collateralToken.balanceOf(msg.sender));
            if (amount > 0) {
                state.withdrawUnderlyingCollateralToken(msg.sender, params.to, amount);
            }
        }

        emit Events.Withdraw(params.token, params.to, amount);
    }
    ```

From the code above we know that whether we take `underlyingCollateralToken` or `underlyingBorrowToken` will check `validateUserIsNotBelowOpeningLimitBorrowCR()` `==>` `collateralRatio() > openingLimitBorrowCR`.

This makes sense for taking `underlyingCollateralToken`, but not for taking `underlyingBorrowToken`.

  1. Taking the `underlyingBorrowToken` does not affect the `collateralRatio`.
  2. The user has already borrowed the funds (with interest accrued and collateralized), it is the user’s asset, and should be able to be withdrawn at will, even if it may be liquidated.
  3. `openingLimitBorrowCR` is still far from being liquidated, and should not restrict the user from withdrawing the borrowed token.

## Recommendation
```solidity
function withdraw(WithdrawParams calldata params) external payable override(ISize) whenNotPaused {
    state.validateWithdraw(params);
    state.executeWithdraw(params);
    if (params.token != address(state.data.underlyingBorrowToken)) {
        state.validateUserIsNotBelowOpeningLimitBorrowCR(msg.sender);
    }
}
```
