# [H] Improperly checked IDs on itemstacks received from the client leading to server crash in PocketMine-MP

## Summary
Severity: High
Advisory: GHSA-fqx3-r75h-vc89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-07
Source: https://github.com/advisories/GHSA-fqx3-r75h-vc89
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.0.0-BETA5 <4.4.2

## Details
### Impact
Due to a workaround for unmapped network items implemented in 4.0.0-BETA5 (8ac16345a3bc099b62c1f5cfbf3b736e621c3f76), arbitrary item IDs are able to be written into an item's NBT. The intended purpose of this is to make said unmapped network items able to be moved around the inventory without issues.

This led to an exploit due to internal limits on the range that item IDs can occupy (-32768 - 32767), while the tag type used to represent the replacement IDs for unknown items is a `TAG_Int`, allowing a range from -(2^31) - 2^31 - 1. This leads to an uncaught exception which crashes the server.

### Patches
5fd685e07d61ef670584ed11a52fd5f4b99a81a7

### Workarounds
In theory this can be checked by plugins using a custom `TypeConverter`, but this is likely to be very cumbersome.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-fqx3-r75h-vc89
- https://github.com/pmmp/PocketMine-MP/commit/5fd685e07d61ef670584ed11a52fd5f4b99a81a7
- https://github.com/pmmp/PocketMine-MP/commit/8ac16345a3bc099b62c1f5cfbf3b736e621c3f76
- https://github.com/pmmp/PocketMine-MP
