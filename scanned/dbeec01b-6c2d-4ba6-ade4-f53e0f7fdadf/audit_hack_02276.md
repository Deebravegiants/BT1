# [M] Lack of event emission

## Summary
Severity: Medium
Source: https://github.com/OriginProtocol/ousd-governance/blob/2b9761606d4ac4062b69367ebbad88220cea45ce/contracts/RewardsSource.sol#L122
Type: audit-issue

## Details
The following functions do not emit relevant events after executing sensitive actions:

* The [setRewardsTarget function](https://github.com/OriginProtocol/ousd-governance/blob/2b9761606d4ac4062b69367ebbad88220cea45ce/contracts/RewardsSource.sol#L122) changes the address `OGV` [tokens are minted to](https://github.com/OriginProtocol/ousd-governance/blob/2b9761606d4ac4062b69367ebbad88220cea45ce/contracts/RewardsSource.sol#L44) as part of the staking reward system.
* The [setInflation function](https://github.com/OriginProtocol/ousd-governance/blob/2b9761606d4ac4062b69367ebbad88220cea45ce/contracts/RewardsSource.sol#L95) deletes and optionally updates the rewards slopes.

Consider emitting events after sensitive changes take place to facilitate tracking and notify off-chain clients following the contracts’ activity.

**Update**: _Fixed in pull request [#96](https://github.com/OriginProtocol/ousd-governance/pull/96/). In addition, consider indexing the event parameters._
