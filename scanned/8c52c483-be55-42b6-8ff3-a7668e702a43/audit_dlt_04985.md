# [H] Missing updating of the `unit` value.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/43
Type: sherlock-finding

## Details
Ch_301

high

# Missing updating of the `unit` value.

## Summary
Missing updating of the `unit` value.

## Vulnerability Detail
On `TimeLockPool.sol` == > `setCurvePoint()`
When the `Gov` decide to add a point to the `curve` or remove the last point of the `curve`

```
        } else if (_position == curve.length) {
            curve.push(_newPoint);
        } else {
            if (curve.length - 1 < 2) {
                revert ShortCurveError();
            }
            curve.pop();
        }
```
There is no updating to the `unit` value
We can see here how the  `unit` is calculating 
```
 unit = maxLockDuration / (curve.length - 1);
```
So any change in the `curve.length` will affect the `unit` value which means `getMultiplier()` will return the wrong value.

## Impact
`getMultiplier()` will deliver a wrong `multiplier` value
And this will affect the `share`s calculation on `deposit()`
```
uint256 mintAmount = _amount * getMultiplier(duration) / 1e18;
``` 

## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/43_
