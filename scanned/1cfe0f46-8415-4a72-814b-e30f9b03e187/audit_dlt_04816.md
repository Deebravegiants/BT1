# [M] Calling startCooldown() directly can bypass the msg.sender restriction in settle()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/28
Type: sherlock-finding

## Details
8olidity

medium

# Calling startCooldown() directly can bypass the msg.sender restriction in settle()

## Summary
Calling startCooldown() directly can bypass the msg.sender restriction in settle()
## Vulnerability Detail
The `msg.sender` is restricted to `lastRoller` in `settle()`, but the user can bypass the restriction in `settle()` by calling `startCooldown() `directly.  Re-set variables to defaults

```solidity
    function startCooldown() public { 
        require(divider.mscale(address(adapter), maturity) != 0);

        ERC20[] memory tokens = new ERC20[](2);
        tokens[1 - pti] = asset;
        tokens[pti    ] = pt;

        _exitPool(
            poolId,
            BalancerVault.ExitPoolRequest({
                assets: tokens,
                minAmountsOut: new uint256[](2),
                userData: abi.encode(space.balanceOf(address(this))),
                toInternalBalance: false
            })
        );

        divider.redeem(address(adapter), maturity, pt.balanceOf(address(this))); // Burns the PTs.
        yt.collect(); // Burns the YTs.

        // Calculate the initial market fixed rate for the upcoming series, using the historical avg Target rate across the previous series.
        targetedRate = utils.getNewTargetedRate(targetedRate, address(adapter), maturity, space);

        maturity   = MATURITY_NOT_SET;
        lastSettle = uint32(block.timestamp);
        delete pt; delete yt; delete space; delete pti; delete poolId; delete initScale; // Re-set variables to defaults, collect gas refund.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/28_
