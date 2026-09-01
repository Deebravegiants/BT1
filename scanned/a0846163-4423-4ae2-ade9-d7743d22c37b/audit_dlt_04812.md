# [M] lastRoller cannot call settle if the AutoRoller contract does not have "stakeSize" amount of adapter's stake token

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/34
Type: sherlock-finding

## Details
ctf_sec

medium

# lastRoller cannot call settle if the AutoRoller contract does not have "stakeSize" amount of adapter's stake token

## Summary

lastRoller cannot call settle if the AutoRoller contract does not have stakeSize amount of stake type token

## Vulnerability Detail

When the lastRoller can settle, thie code runs:

```solidity
  /// @notice Settle the active Series, transfer stake and ifees to the settler, and enter a cooldown phase.
  /// @dev Because the auto-roller is the series sponsor from the Divider's perspective, this.settle is the only entrypoint for athe lastRoller to settle during the series' sponsor window.
  ///      More info on the series lifecylce: https://docs.sense.finance/docs/series-lifecycle-detail/#phase-3-settling.
  function settle() public {
      if(msg.sender != lastRoller) revert InvalidSettler();

      uint256 assetBalPre = asset.balanceOf(address(this));
      divider.settleSeries(address(adapter), maturity); // Settlement will fail if maturity hasn't been reached.
      uint256 assetBalPost = asset.balanceOf(address(this));

      asset.safeTransfer(msg.sender, assetBalPost - assetBalPre); // Send issuance fees to the sender.

      (, address stake, uint256 stakeSize) = adapter.getStakeAndTarget();
      if (stake != address(asset)) {
          ERC20(stake).safeTransfer(msg.sender, stakeSize);
      }

      startCooldown();
  }
```

note this section.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/34_
