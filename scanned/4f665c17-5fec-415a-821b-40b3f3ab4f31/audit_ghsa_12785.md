# [H] PocketMine-MP has improperly handled dye colour IDs in banner NBT, leading to server crash

## Summary
Severity: High
Advisory: GHSA-wqqv-jcfr-9f5g
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-wqqv-jcfr-9f5g
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.8.1

## Details
### Impact
`DyeColorIdMap->fromId()` did not account for the possibility that it might be given invalid input. This means that an undefined offset error would occur whenever this happened.

This code is indirectly called during [`Banner->deserializeCompoundTag()`](https://github.com/pmmp/PocketMine-MP/blob/38d6284671e8b657ba557e765a6c29b24a7705f5/src/item/Banner.php#L104), which is invoked when deserializing any item NBT, whether from network or disk.

An attacker could use this bug to crash a server by providing NBT with invalid values for pattern colours in an inventory transaction, or by using `/give` to obtain an item with NBT like this.

### Patches
08b9495bce2d65a6d1d3eeb76e484499a00765eb

### Workarounds
This is quite difficult to work around via a plugin. Theoretically, it's possible to override the `Banner` item class from a plugin and validate the data before it reaches `deserializeCompoundTag()`.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@pmmp.io](mailto:security@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-wqqv-jcfr-9f5g
- https://github.com/pmmp/PocketMine-MP/commit/08b9495bce2d65a6d1d3eeb76e484499a00765eb
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/38d6284671e8b657ba557e765a6c29b24a7705f5/src/item/Banner.php#L104
