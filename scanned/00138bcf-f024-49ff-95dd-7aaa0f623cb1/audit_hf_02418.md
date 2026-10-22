# [H] Potential Misuse of Borrow Allowance in LenderVault

## Summary
Severity: High
Contest weight: 0.6266
Dataset id: 13014
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Shoebill protocol has a LenderVaults contract that accepts user deposits and interacts directly with the underlying lending protocol. While examining the borrow-related operation, we notice the vault supports the onBehalfOf feature that requires the borrowing users to pre-approve the borrow allowance. Our analysis shows this feature may be misused to borrow on behalf of other approving innocent users. In particular, if we show below the borrow-related implementation of borrow(), we notice the last argument is onBehalfOf, which is directly provided by the user. Since the LenderVaults contract interacts directly with the lending protocol, from the lending protocol perspective, it will consider the user approves the borrow on the LenderVaults contract, not the calling user. As a result, a malicious actor may abuse the trust to directly borrow funds from other approving users, who may not approve on the malicious actor!

```solidity
function borrow(
    address _external,
    uint256 _amount,
    uint256 interestRateMode, // 2 = variable
    uint16 referralCode, // 0 default
    address onBehalfOf
) external virtual {
    _updateliquidity();
    uint256 _internalAssetAmount = _getInternalAmount(_external, _amount);
    uint256 beforeBorrow = IERC20(internalAssetToken).balanceOf(address(this));
    ILendingPool(_addressesProvider.getLendingPool()).borrow(
        internalAssetToken,
        _internalAssetAmount,
        interestRateMode,
        referralCode,
        onBehalfOf
    );
    uint256 afterBorrow = IERC20(internalAssetToken).balanceOf(address(this));
    uint256 _amountToWithdraw = afterBorrow - beforeBorrow;
    uint256 withdrawAmount = _withdrawFromYieldPool(_external, _amountToWithdraw, onBehalfOf);
    require(withdrawAmount >= _amount, Errors.VT_WITHDRAW_AMOUNT_MISMATCH);
}
```

## Recommendation
Revisit the above approval issue to avoid being misused.
