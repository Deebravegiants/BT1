# [M] TradingLimits::update() incor-

## Summary
Severity: Medium
Contest weight: 0.5896
Dataset id: 1760
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TradingLimits::update() divides the traded funds by the decimals of the token, int256 _deltaFlowUnits = _deltaFlow / int256((10 ** uint256(decimals)));. In a token with 18 decimals,
for example, swapping 1.999...e18 tokens will lead to a _deltaFlowUnits of just 1, taking a
major error. This can be exploited to swap up to twice the trading limit, if tokens are
swapped 2 by 2 and the state is updated only by 1 each time. Overall, even without
malicious intent, the limits will always be bypassed due to the rounding.
In TradingLimits:135, it only rounds up whenever deltaFlowUnits becomes 0, but the
error is just as big if it becomes 1 from 2, effectively not providing enough protection.
Internal pre-conditions
None.
External pre-conditions
None.
Attack Path
1. User calls Broker::swapIn/Out() with amounts in and out that produce rounding
errors (almost always).
The trading limits may be severely bypassed with malicious intent (by double the
amount) or by a smaller but still significant amount organically.

## Proof of Concept
TradingLimits::update() only rounds up when deltaFlowUnits becomes 0.
```solidity
function update(
    ITradingLimits.State memory self,
    ITradingLimits.Config memory config,
    int256 _deltaFlow,
    uint8 decimals
) internal view returns (ITradingLimits.State memory) {
    int256 _deltaFlowUnits = _deltaFlow / int256((10 ** uint256(decimals)));
    require(_deltaFlowUnits <= MAX_INT48, "dFlow too large");
    int48 deltaFlowUnits = int48(_deltaFlowUnits);
    if (deltaFlowUnits == 0) {
        deltaFlowUnits = _deltaFlow > 0 ? int48(1) : int48(-1);
    }
    ...
}
```

## Recommendation
The correct fix is:
```solidity
int256 _deltaFlowUnits = (_deltaFlow - 1) / int256((10 ** uint256(decimals))) + 1;
```
