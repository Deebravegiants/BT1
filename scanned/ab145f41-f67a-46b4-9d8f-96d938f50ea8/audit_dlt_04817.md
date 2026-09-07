# [M] use safetransfer()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/27
Type: sherlock-finding

## Details
8olidity

medium

# use safetransfer()

## Summary
use safetransfer()
## Vulnerability Detail
use safetransfer() instead of transfer() for token transfers

This is especially true of the `claimRewards()` function, as the coin address is not controllable

```solidity
	// contracts/src/AutoRoller.sol
    function eject(
        uint256 shares,
        address receiver,
        address owner
    ) public returns (uint256 assets, uint256 excessBal, bool isExcessPTs) {
        if (maturity == MATURITY_NOT_SET) revert ActivePhaseOnly();

        if (msg.sender != owner) {
            uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

            if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
        }

        (excessBal, isExcessPTs) = _exitAndCombine(shares);

        _burn(owner, shares); // Burn after percent ownership is determined in _exitAndCombine.

        if (isExcessPTs) {
            pt.transfer(receiver, excessBal);
        } else {
            yt.transfer(receiver, excessBal);
        }

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/27_
