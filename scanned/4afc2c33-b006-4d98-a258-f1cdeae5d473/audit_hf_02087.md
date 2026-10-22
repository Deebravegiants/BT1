# [M] Missing Authentication for Critical Functions in Strategy Contracts

## Summary
Severity: Medium
Contest weight: 0.4323
Dataset id: 11784
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the StrategyPickleUSDC contract, the Controller is allowed to withdraw() arbitrary amount of USDC from Curve. In particular, after withdrawing enough 3Crv tokens, the withdrawUnderlying() function is called to remove_liquidity() from the 3Crv pool and exchange all assets into USDC.
```solidity
function withdrawUnderlying(uint256 _amount)
    public
    returns (uint)
{
    IERC20(crvPla).safeApprove(curvefi, 0);
    IERC20(crvPla).safeApprove(curvefi, _amount);
    uint _before = IERC20(want).balanceOf(address(this));
    ICurveFi(curvefi).remove_liquidity(_amount, [0, uint256(0), 0]);
    uint256 _ydai = IERC20(ydai).balanceOf(address(this));
    uint256 _yusdt = IERC20(yusdt).balanceOf(address(this));
    if (_ydai > 0) {
        IERC20(ydai).safeApprove(curvefi, 0);
        IERC20(ydai).safeApprove(curvefi, _ydai);
        ICurveFi(curvefi).exchange(0, 1, _ydai, 0);
    }
    if (_yusdt > 0) {
        IERC20(yusdt).safeApprove(curvefi, 0);
        IERC20(yusdt).safeApprove(curvefi, _yusdt);
        ICurveFi(curvefi).exchange(2, 1, _yusdt, 0);
    }
    uint _after = IERC20(want).balanceOf(address(this));
    return _after.sub(_before);
}
```
However, this crucial withdrawUnderlying() function is deﬁned as a public function, which allows bad actors to impersonate the privileged Controller to convert 3Crv into USDC whenever the strategy contract has 3Crv balance. The same issue is also applicable to the StrategyPickleWBTC contract.

## Recommendation
Make withdrawUnderlying() an internal function or authenticate the caller.
