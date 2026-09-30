# [H] \[H01\] Bond penalty may not apply

## Summary
Severity: High
Source: https://github.com/UMAprotocol/protocol/blob/1631ef7ad29aaeba756ef3b9a01c667e1343df85/packages/core/contracts/oracle/implementation/OptimisticOracle.sol#L549-L549
Type: audit-issue

## Details
The optimistic oracle is designed so that in the event of a dispute, [the incorrect party pays the bond penalty to the vindicated party](https://github.com/UMAprotocol/protocol/blob/1631ef7ad29aaeba756ef3b9a01c667e1343df85/packages/core/contracts/oracle/implementation/OptimisticOracle.sol#L549-L549), as determined by the DVM. However, if the proposer and disputer are the same entity, this transfer has no effect. The only remaining deterrent is the DVM fee. Since the bond size is specifically chosen to dissuade attackers from submitting the wrong price and delaying resolution, the ability to nullify the bond penalty undermines the economic reasoning. Moreover, if the reward exceeds the DVM fee, the attacker may actually be positively rewarded for delaying the resolution.

This attack does not apply to contracts deployed from the Perpetual Multiparty template, because they disregard disputed price requests. Nevertheless, it does limit the simplicity and applicability of the optimistic oracle. Consider burning some or all of the bond penalty and ensuring the reward is not high enough to compensate.

**Update**: _Fixed in [PR#2329](https://github.com/UMAprotocol/protocol/pull/2329) and [PR#2429](https://github.com/UMAprotocol/protocol/pull/2429). If the `finalFee` associated with the request is non-zero, half the bond is added to the fee and sent to the UMA `Store`. Naturally, this reduces the amount paid to the vindicated party._
