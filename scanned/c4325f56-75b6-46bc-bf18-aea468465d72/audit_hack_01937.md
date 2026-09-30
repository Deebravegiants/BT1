# [M] 5.2 Zero Address Reward Distributor

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Acknowledged

The add_reward functions in all gauge contracts do not check that the _distributor address is not
the zero address. This is problematic as set_reward_distributor asserts that the distributor
address is not zero. Therefore, if add_reward is called with the zero address as the _distributor
parameter, a reward distributor can never be set for this reward token entry.

Acknowledged

StakeDAO acknowledges the issue without changes as they rate the chances as very low that the
described issue happens. They state the issue only occurs when they add a reward distributor manually
to the LiquidityGaugeV4.
