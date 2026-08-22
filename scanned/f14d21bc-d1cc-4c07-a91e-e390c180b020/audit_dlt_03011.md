# [M] updatePeriod() less mint HERMES

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-maia
Published: 2023-07-05
Source: https://github.com/code-423n4/2023-05-maia-findings/issues/737
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/hermes/minters/BaseV2Minter.sol#L139-L141


# Vulnerability details

## Impact
If there is a `weekly` that has not been taken, it may result in insufficient mint HERMES

## Proof of Concept
In `updatePeriod()`, mint new `HERMES` every week with a certain percentage `weeklyEmission`.


The code is as follows.

```solidity
    function updatePeriod() public returns (uint256) {
        uint256 _period = activePeriod;
        // only trigger if new week
        if (block.timestamp >= _period + week && initializer == address(0)) {
            _period = (block.timestamp / week) * week;
            activePeriod = _period;
            uint256 newWeeklyEmission = weeklyEmission();
@>          weekly += newWeeklyEmission;
            uint256 _circulatingSupply = circulatingSupply();

            uint256 _growth = calculateGrowth(newWeeklyEmission);
            uint256 _required = _growth + newWeeklyEmission;
            /// @dev share of newWeeklyEmission emissions sent to DAO.
            uint256 share = (_required * daoShare) / base;
            _required += share;
            uint256 _balanceOf = underlying.balanceOf(address(this));          
@>          if (_balanceOf < _required) {
                HERMES(underlying).mint(address(this), _required - _balanceOf);
            }

            underlying.safeTransfer(address(vault), _growth);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-maia-findings/issues/737_
