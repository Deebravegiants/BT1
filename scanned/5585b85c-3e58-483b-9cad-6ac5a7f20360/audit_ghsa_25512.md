# [H] Insufficient type validation in pocketmine/pocketmine-mp

## Summary
Severity: High
Advisory: GHSA-g5rr-p69h-7v3g
CWE: CWE-1287, CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-g5rr-p69h-7v3g
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.2.9

## Details
### Impact
When an inventory interaction is performed (e.g. moving an item around an inventory), the client sends a serialized version of the itemstack to the server, which the server then deserializes and compares against its own copy. If the copies don't match, the transaction is invalid.

This involves deserializing item NBT from the client, which allows for bogus data to be provided. Usually, this is harmless, but in this particular case, it could result in crashes on certain types of bad data (e.g. incorrect ListTag type provided for the `CanDestroy` tag).

### Patches
This is fixed in 4.2.9 by commit 5a98b08ee8dc8ff14862cd83d2e4af9d212fefc2.

### Workarounds
It's non-trivial to workaround this, but can be done by handling `InventoryTransactionPacket` and `PlayerAuthInputPacket` to scrub inbound transaction data of bogus NBT that would cause these crashes.

### For more information
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-g5rr-p69h-7v3g
- https://github.com/pmmp/PocketMine-MP/commit/5a98b08ee8dc8ff14862cd83d2e4af9d212fefc2
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/4.2.9/changelogs/4.2.md#429
- https://github.com/pmmp/PocketMine-MP/releases/tag/4.2.9
