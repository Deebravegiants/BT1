# [H] `_debt_interest_since_last_update` calculation uses `PERCENTAGE_BASE` instead of `PERCENTAGE_BASE_HIGH_PRECISION`

## Summary
Severity: High
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1069-L1076
Type: audit-issue

## Details
# `_debt_interest_since_last_update` calculation uses `PERCENTAGE_BASE` instead of `PERCENTAGE_BASE_HIGH_PRECISION`

## Summary
`_debt_interest_since_last_update` calculation uses `PERCENTAGE_BASE` instead of `PERCENTAGE_BASE_HIGH_PRECISION`, leading to an interest rate 1000x larger than intended.

## Vulnerability Detail
Interest accrued since last update calculation is using `PERCENTAGE_BASE` as base percentage of `_current_interest_per_second`:

[Vault.vy#L1069-L1076](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1069-L1076)
```solidity
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
        / PERCENTAGE_BASE
        / PRECISION
    )
```

Following this path `_current_interest_per_second`:

[Vault.vy#L1173-L1179](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1173-L1179)
```solidity
def _current_interest_per_second(_debt_token: address) -> uint256:
    utilization_rate: uint256 = self._utilization_rate(_debt_token) 
    interest_rate: uint256 = self._interest_rate_by_utilization(
        _debt_token, utilization_rate
    )
    interest_per_second: uint256 = interest_rate * PRECISION / SECONDS_PER_YEAR
    return interest_per_second
```

Then, `_interest_rate_by_utilization`:

[Vault.vy#L1204-L1220](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1204-L1220)
```solidity
def _interest_rate_by_utilization(
    _address: address, _utilization_rate: uint256
) -> uint256:
    """
    @notice
        we have two tiers of interest rates that are linearily growing from
        _min_interest_rate to _mid_interest_rate and _mid_interest_rate to
        _max_interest_rate respectively. The switch between both occurs at
        _rate_switch_utilization


        note: the slope of the first line must be lower then the second line, if
        not the contact will revert
    """
    if _utilization_rate < self._rate_switch_utilization(_address):
        return self._dynamic_interest_rate_low_utilization(_address, _utilization_rate)
    else:
        return self._dynamic_interest_rate_high_utilization(_address, _utilization_rate)
```

Then, `_dynamic_interest_rate_high_utilization`:

[Vault.vy#L1253-L1276](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1253-L1276)
```solidity
def _dynamic_interest_rate_high_utilization(
    _address: address, _utilization_rate: uint256
) -> uint256:
    # if it's smaller switch zero we return the min-interest-rate without
    # calculation
    if _utilization_rate < self._rate_switch_utilization(_address):
        return self._mid_interest_rate(_address)


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

We can see that interest rate are determined by the utilization rate and are denominated in `PERCENTAGE_BASE_HIGH_PRECISION` as shown by this slope calculation in `_dynamic_interest_rate_high_utilization` (with `FULL_UTILIZATION == 100_00_000`). Because the slope is in denominated in `PRECISION` the other numerator and the denominator have to be of the same nature:

[Vault.vy#L1264-L1268](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1264-L1268)
```solidity
_slope: uint256 = (
        (self._max_interest_rate(_address) - self._mid_interest_rate(_address))
        * PRECISION
        / (FULL_UTILIZATION - self._rate_switch_utilization(_address))
    )
```

## Impact
The interest rate will be 1000x larger than intended.

## Code Snippet
See above.

## Tool used

Manual Review

## Recommendation
Consider modifying the code like this:

```solidity
def _debt_interest_since_last_update(_debt_token: address) -> uint256:
    return (
        (block.timestamp - self.last_debt_update[_debt_token])
        * self._current_interest_per_second(_debt_token)
        * self.total_debt_amount[_debt_token]
-       / PERCENTAGE_BASE
+       / PERCENTAGE_BASE_HIGH_PRECISION
        / PRECISION
    )
```
