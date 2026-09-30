# [M] Proper EMode Category Use in Pool::borrow()

## Summary
Severity: Medium
Contest weight: 0.4372
Dataset id: 11568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Aave protocol has a nice feature credit delegation, which allows a credit delegator to delegate the credit of their account's position to a borrower.
This feature requires proper accounting of delegation allowance and actual expenditure. While examining its implementation, we notice a key function borrow() does not properly follow the credit delegation logic.
To elaborate, we show below this borrow() function. This is a core lending function and is used to borrow funds from the lending protocol. It comes to our attention that the encapsulated DataTypes.ExecuteBorrowParams parameters mistakenly uses _usersEModeCategory[msg.sender] as the user's eMode category. In the credit delegation situation, the real eMode category should be _usersEModeCategory[onBehalfOf].
```solidity
/// @inheritdoc IPool
function borrow(
    address asset,
    uint256 amount,
    uint256 interestRateMode,
    uint16 referralCode,
    address onBehalfOf
) external override {
    BorrowLogic.executeBorrow(
        _reserves,
        _reservesList,
        _eModeCategories,
        _usersConfig[onBehalfOf],
        DataTypes.ExecuteBorrowParams(
            asset,
            msg.sender,
            onBehalfOf,
            amount,
            interestRateMode,
            referralCode,
            true,
            _maxStableRateBorrowSizePercent,
            _reservesCount,
            _addressesProvider.getPriceOracle(),
            _usersEModeCategory[onBehalfOf],
            _addressesProvider.getPriceOracleSentinel()
        )
    );
}
```

## Recommendation
Ensure the credit delegation feature is consistently honored in all aspects of the lending protocol.
