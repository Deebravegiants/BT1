# [H] Improper withdraw() Logic in LendingPool

## Summary
Severity: High
Contest weight: 0.6289
Dataset id: 12787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pluz is a permissionless lending protocol that allows users to have a leveraged access on their collateral. The lending pool is implemented in a core contract named LendingPool. While examining the lending support, we notice current implementation on collateral withdrawal and debt repayment can be improved. In the following, we show the implementation of the related withdraw() routine. This routine allows an user to withdraw his or her collateral. However, it comes to our attention that the actual asset amount for withdrawal (convertAmount) may be prematurely computed as _convertAmount(amountToWithdraw, IERC20Rebasing(address(reserve.asset))) (line 233). The reason is that the given variable of amountToWithdraw may be later updated when the input amount is larger than the user balance (line 241). With that, there is a need to compute the actual asset amount convertAmount after the amountToWithdraw is finalized (line 242).
```solidity
function withdraw(uint256 amount) public virtual whenNotPaused nonReentrant returns(uint256) {
    uint256 amountToWithdraw = amount;
    uint256 convertAmount = _convertAmount(amountToWithdraw, IERC20Rebasing(address(reserve.asset)));
    _beforeAction();
    bool isMaxWithdraw = false;
    uint256 userBalance = liquidityToken.balanceOf(msg.sender);
    if (amount >= userBalance) {
        amountToWithdraw = userBalance;
        isMaxWithdraw = true;
    }
    reserve.assetBalance -= amountToWithdraw;
    liquidityToken.burn(msg.sender, amountToWithdraw, reserve.liquidityIndex, isMaxWithdraw, MathUtils.ROUNDING.UP);
    IERC20Rebasing(address(reserve.asset)).unwrap(amountToWithdraw);
    _actualAsset.safeTransfer(msg.sender, convertAmount);
    _mintToTreasury();
    _updateInterestRate();
    emit Withdraw(msg.sender, amountToWithdraw);
    return amountToWithdraw;
}
```

## Recommendation
Improve the above-mentioned routine to properly compute the actual asset amount for withdrawal. Note the same issue is also applicable to the repay() routine from the same contract.
