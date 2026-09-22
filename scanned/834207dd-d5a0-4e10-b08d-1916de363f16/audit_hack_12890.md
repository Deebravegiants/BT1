# [H] `_dynamic_interest_rate_high_utilization` doesn’t preserve continuity

## Summary
Severity: High
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1261-L1276
Type: audit-issue

## Details
# `_dynamic_interest_rate_high_utilization` doesn’t preserve continuity

## Summary

## Vulnerability Detail
The calculation done in `_dynamic_interest_rate_high_utilization` is wrong and doesn't preserve continuity with the pre-kink line-equation:

[Vault.vy#L1261-L1276](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1261-L1276)
```solidity
		# default line-equation y = mx + d where m is _slope, x is _utilization_rate
    # and m  is _diff
    # thus y = _slope * _utilization_rate -_diff
    _slope: uint256 = (
        (self._max_interest_rate(_address) - self._mid_interest_rate(_address))
        * PRECISION
        / (FULL_UTILIZATION - self._rate_switch_utilization(_address))
    )


    _diff: uint256 = (
        _slope * PERCENTAGE_BASE_HIGH_PRECISION
        - self._max_interest_rate(_address) * PRECISION
    )
    _additional_rate_through_utilization: uint256 = _slope * _utilization_rate - _diff


    return _additional_rate_through_utilization / PRECISION
```

The problem is in the `_diff` variable calculation. Using the line-equation as it is written `_slope * _utilization_rate - _diff` we can solve at `_utilization_rate == _rate_switch_utilization` for `_mid_interest_rate`: 

-> `_slope * _rate_switch_utilization - _diff = _mid_interest_rate`
-> `_slope * _rate_switch_utilization - _mid_interest_rate = _diff`

Therefore, `_diff` should be:

```solidity
    _diff: uint256 = (
        _slope * _rate_switch_utilization
        - self._mid_interest_rate(_address) * PRECISION
    )
```

## Impact
Interest rate will get miscalculated and lead to different interest rates than expected.

## Code Snippet
See above.

## Tool used

Manual Review

## Recommendation
Consider this other way of doing it which is clearer in my opinion:

At a given `_rate_switch_utilization` the interest rate should be `_mid_interest_rate`, therefore the y-intercept of the line-equation should be `_mid_interest_rate` and the x value should be 0 instead of `_utilization_rate`. To achieve this `d` should be equal to `_mid_interest_rate`, `x` to `_utilization_rate - self._rate_switch_utilization(_address)` and the slope `m` is the same.
Additionally, `_additional_rate_through_utilization` should be written `_slope * _utilization_rate + y-intercept` with a plus sign.
