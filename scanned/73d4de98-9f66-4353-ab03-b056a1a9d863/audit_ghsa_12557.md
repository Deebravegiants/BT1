# [M] PocketMine MP vulnerable to uncontrolled resource consumption via mismatched type of 'InventoryTransactionPacket'

## Summary
Severity: Medium
Advisory: GHSA-42qm-8v8m-m78c
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-06-01
Source: https://github.com/advisories/GHSA-42qm-8v8m-m78c
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.18.0-ALPHA2

## Details
### Impact
A "mismatch" type `InventoryTransactionPacket` is sent by the client to request a resync of all currently open inventories.

Since PocketMine-MP does not rate-limit these "mismatch" transactions, and the syncing of inventories is not deferred until, e.g. the end of the current tick, they can be used as a very cheap bandwidth multiplier by making the server send out many MB of data (network serialized inventory items can be very large, especially when dealing with large amounts of NBT).

This is not currently known to have been exploited in the wild.

### Patches
This problem was fixed in 4.18.0-ALPHA2 by ca6d51498f12427a947467da8fcad7811418e6cc alongside the introduction of the `ItemStackRequest` system implementation.

### Workarounds
Plugins can handle `DataPacketReceiveEvent` for `InventoryTransactionPacket` and check if the type is `MismatchTransactionData`. If it is, apply some kind of rate limit (e.g. max 1 per tick).

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-42qm-8v8m-m78c
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/4.18.0-ALPHA2/changelogs/4.18-alpha.md#4180-ALPHA2
