# [H] Uncapped length of skin data fields submitted by players

## Summary
Severity: High
Advisory: GHSA-c6fg-99pr-25m9
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-c6fg-99pr-25m9
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <3.26.5
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.0.0 <4.0.5

## Details
### Impact
Some skin data fields (e.g. skinID, geometryName) are not capped in length. These fields are typically saved in the NBT data of a player when the player quits the server, or during an autosave.

This is problematic due to the 32767 byte limit on `TAG_String`s. If any of these fields exceeds 32767 bytes, an exception will be thrown during data saving, which will cause the server to crash.

Other fields (such as skinGeometryData) are also uncapped, but those have a much larger 2 GB length limit, so this is not a concern for those, particularly considering the decompressed packet size limit of 2 MB.

### Patches
PM3: 958a9dbf0fe3131ab60319c5a939f5dfbfe5dfbb
PM4: 6492cac5c10f9fa8443ceddd2191a7b65b73f601

### Workarounds
A plugin may check player skins during `PlayerLoginEvent` and `PlayerSkinChangeEvent` and ensure that the offending fields are not larger than 32767 bytes.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-c6fg-99pr-25m9
- https://github.com/pmmp/PocketMine-MP/commit/6492cac5c10f9fa8443ceddd2191a7b65b73f601
- https://github.com/pmmp/PocketMine-MP/commit/958a9dbf0fe3131ab60319c5a939f5dfbfe5dfbb
- https://github.com/pmmp/PocketMine-MP
