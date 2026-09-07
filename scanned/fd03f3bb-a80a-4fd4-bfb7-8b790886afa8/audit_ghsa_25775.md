# [H] Improperly checked metadata on tools/armour itemstacks received from the client

## Summary
Severity: High
Advisory: GHSA-46c5-pfj8-fv65
CWE: CWE-704
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-46c5-pfj8-fv65
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.2.4

## Details
### Impact
Due to a workaround applied in 1.13, an attacker may send a negative damage/meta value in a tool or armour item's NBT, which `TypeConverter` then blindly uses as if it was valid without being checked.

When this invalid metadata value reaches `Durable->setDamage()`, an exception is thrown because the metadata is not within the expected range for damage values.

This can be reproduced with either a too-large damage value, or a negative one.

### Patches
c8e1cfcbee4945fd4b63d2a7e96025c59744d4f1

### Workarounds
In theory this can be checked by plugins using a custom `TypeConverter`, but this is likely to be very cumbersome.

### For more information
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-46c5-pfj8-fv65
- https://github.com/pmmp/PocketMine-MP/commit/c8e1cfcbee4945fd4b63d2a7e96025c59744d4f1
- https://github.com/pmmp/PocketMine-MP
