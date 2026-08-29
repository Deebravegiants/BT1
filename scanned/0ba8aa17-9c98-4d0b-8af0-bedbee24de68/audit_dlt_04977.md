# [H] Depositors will never get the highest bonus after a new point is added to the end of a curve

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/57
Type: sherlock-finding

## Details
Jeiwan

medium

# Depositors will never get the highest bonus after a new point is added to the end of a curve

## Summary
When adding new points to a curve, it's required to update the [unit](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L25) state variable. This is done correctly in the [setCurve](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L280) function, but not in the [setCurvePoint](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L322) function. Thus, when a point is added to the end of a curve (such point is supposed to be a point with the highest bonus) the highest bonus will never be applied to deposited amounts because [maxLockDuration / uni](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L238) will never be equal to the new point's index.
## Vulnerability Detail
The root cause is that the [setCurvePoint](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L322) function never updates `unit` after adding a point to the end of the curve:
```solidity
function setCurvePoint(uint256 _newPoint, uint256 _position) external onlyGov {
    if (_newPoint > maxBonus) {
        revert MaxBonusError();
    }
    if (_position < curve.length) {
        curve[_position] = _newPoint;
    } else if (_position == curve.length) {
        curve.push(_newPoint); // @audit unit is not updated after a new point was added
    } else {
        if (curve.length - 1 < 2) {
            revert ShortCurveError();
        }
        curve.pop();
    }
    emit CurveChanged(_msgSender());
}
```
## Impact
Users will never get the highest bonus if a new point is added to the curve, which undermines the trust in the protocol since the protocol guarantees highest bonus for maximal duration depositors.
## Code Snippet
```javascript
// test/TimeLockPool.ts
it("doesn't update unit after adding a point [audit]", async () => {
    const maxDuration = await timeLockPool.maxLockDuration();

    // The maximal multiplier is 6e18
    expect(await timeLockPool.getMultiplier(maxDuration)).to.eq(constants.WeiPerEther.mul(6));
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/57_
