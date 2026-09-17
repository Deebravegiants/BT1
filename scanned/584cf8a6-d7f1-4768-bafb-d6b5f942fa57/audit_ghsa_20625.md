# [H] PocketMine-MP invalid skin geometry JSON data leading to server crash

## Summary
Severity: High
Advisory: GHSA-8cwq-4cmf-px73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-8cwq-4cmf-px73
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.7.2

## Details
### Impact
`pocketmine\entity\Skin` doesn't correctly handle errors produced by `adhocore/json-comment`, which throws `RuntimeException` rather than returning `false` as PocketMine-MP expects.

This leads to a server crash if the skin geometry data is invalid for some reason (e.g. a syntax error).

### Patches
c9626c610b8f6810c8c987559c9197b2a291f0bb

### Workarounds
A plugin could handle `LoginPacket` and `PlayerSkinPacket` to verify the skin geometry data can be parsed correctly, so that the error condition in the core code is never reached.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@pmmp.io](mailto:security@example.com)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-8cwq-4cmf-px73
- https://github.com/pmmp/PocketMine-MP/commit/c9626c610b8f6810c8c987559c9197b2a291f0bb
- https://github.com/pmmp/PocketMine-MP
