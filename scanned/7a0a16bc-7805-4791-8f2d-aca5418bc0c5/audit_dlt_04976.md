# [H] Denial of service for maximal bonus depositors after a curve point was removed

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/58
Type: sherlock-finding

## Details
Jeiwan

medium

# Denial of service for maximal bonus depositors after a curve point was removed

## Summary
When removing a point from a curve, it's required to update the [unit](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L25) state variable. This is done correctly in the [setCurve](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L280) function, but not in the [setCurvePoint](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L322) function. Thus, when a point is removed from a curve, trying to deposit at maximal bonus will result in an "Out of bounds" error because [maxLockDuration / unit](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L238) will always result in an index that's outside of the curve array.
## Vulnerability Detail
The root cause is that the [setCurvePoint](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L322) function never updates `unit` after removing a point from a curve:
```solidity
function setCurvePoint(uint256 _newPoint, uint256 _position) external onlyGov {
    if (_newPoint > maxBonus) {
        revert MaxBonusError();
    }
    if (_position < curve.length) {
        curve[_position] = _newPoint;
    } else if (_position == curve.length) {
        curve.push(_newPoint);
    } else {
        if (curve.length - 1 < 2) {
            revert ShortCurveError();
        }
        curve.pop(); // @audit unit is not updated after a point was removed
    }
    emit CurveChanged(_msgSender());
}
```
## Impact
Users won't be able to deposit funds at maximal bonus (with the longest lock duration). Considering that curve points are added or removed by the government after a successful voting (which means the crucial importance of adding/removing the point), this can be considered as an indefinite denial of service.
## Code Snippet
```javascript
// test/TimeLockPool.ts
it("doesn't update unit after removing a point [audit]", async () => {
    const maxDuration = await timeLockPool.maxLockDuration();
    // The maximal multiplier is 6e18
    expect(await timeLockPool.getMultiplier(maxDuration)).to.eq(constants.WeiPerEther.mul(6));

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/58_
