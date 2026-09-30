# [H] Revisited Logic of HegicStrategy::_create()

## Summary
Severity: High
Contest weight: 0.6337
Dataset id: 12221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Hegic Herge protocol, the HegicStrategy contract implements the standard option trading strat-
egy, while some other contracts inheriting from it implement the specific option trading strategies.
In particular, the internal _create() routine called inside the create() routine is used to create a new
option for the user. While examining its logic, we notice there is an improper implementation that
needs to be improved.
To elaborate, we show below the related code snippet of the HegicStrategy contract.
Inside the _create() routine, the calculateNegativepnlAndPositivepnl() routine is called (line 128)
to calculate the positive PNL and negative PNL for the new option.
The first returned value of
the calculateNegativepnlAndPositivepnl() routine is negative PNL and the second returned value is
positive PNL. However, inside the _create() routine, we observe its first returned value is used as
positive PNL and its second returned value is used as negative PNL, which is the opposite of its
implementation. Given this, we suggest to improve the implementation as below: (negativePNL,
positivePNL) = calculateNegativepnlAndPositivepnl(amount, period, additional) (line 128).
```solidity
function _create(
    uint256 id,
    address, /* holder */
    uint256 amount,
    uint256 period,
    bytes[] calldata additional
) internal virtual returns (uint32 expiration, uint256 positivePNL, uint256 negativePNL) {
    (positivePNL, negativePNL) = calculateNegativepnlAndPositivepnl(
        amount,
        period,
        additional
    );
}

function calculateNegativepnlAndPositivepnl(
    uint256 amount,
    uint256 period,
    bytes[] calldata /* additional */
) public view virtual override returns (uint128 negativepnl, uint128 positivepnl) {
    negativepnl = _calculateCollateral(amount, period);
    positivepnl = _calculateStrategyPremium(amount, period);
}
```
Note another routine, i.e., HegicInverseStrategy::_create(), shares the same issue.

## Recommendation
Correct the implementation of the _create() routine as above-mentioned.
