# [H] wrong "unit" setting

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/61
Type: sherlock-finding

## Details
bin2chen

high

# wrong "unit" setting

## Summary
when call setCurvePoint() , no recalculation  "unit" , will cause getMultiplier() to calculate an error points.

## Vulnerability Detail
in TimeLockPool.sol setCurvePoint() , the length of the "curve" can be increased or decreased
but there is no recalculation of the "unit"
If the length of the "curve.length" and the "unit" do not match, the getMultiplier() will be calculated incorrectly , maybe revert "Index out of bounds" or not use the points.

## Impact
when deposit() maybe revert or shares calculation error
## Code Snippet

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L329

``` solidity
    function setCurvePoint(uint256 _newPoint, uint256 _position) external onlyGov {
       ....

        } else if (_position == curve.length) {
            curve.push(_newPoint);    /***** change curve.length *****/
        } else {
            if (curve.length - 1 < 2) {
                revert ShortCurveError();
            }
            curve.pop();  /***** change curve.length *****/
        }
       /*****  no reset of "unit"  ******/
        emit CurveChanged(_msgSender());
    }
```

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/61_
