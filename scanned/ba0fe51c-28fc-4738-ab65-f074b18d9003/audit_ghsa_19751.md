# [M] PocketMine-MP allows malicious client data to waste server resources due to lack of limits for explode()

## Summary
Severity: Medium
Advisory: GHSA-g274-c6jj-h78p
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-g274-c6jj-h78p
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.25.2

## Details
### Impact
Due to lack of limits by default in the [`explode()`](https://www.php.net/manual/en/function.explode.php) function, malicious clients were able to abuse some packets to waste server CPU and memory.

This is similar to a previous security issue published in https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-gj94-v4p9-w672, but with a wider impact, including but not limited to:

- Sign editing
- LoginPacket JWT parsing
- Command parsing

However, the estimated impact of these issues is low, due to other limits such as the packet decompression limit.

### Patches
The issue was fixed in 5.25.2 via d0d84d4c5195fb0a68ea7725424fda63b85cd831.

A custom PHPStan rule has also been introduced to the project, which will henceforth require that all calls to `explode()` within the codebase must specify the `limit` parameter.

### Workarounds
No simple way to fix this.
Given that sign editing is the easiest way this could be exploited, workarounds could include plugins pre-processing `BlockActorDataPacket` to check that the incoming text doesn't have more than 4 parts when split by `\n`.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-g274-c6jj-h78p
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-gj94-v4p9-w672
- https://github.com/pmmp/PocketMine-MP/commit/d0d84d4c5195fb0a68ea7725424fda63b85cd831
- https://github.com/pmmp/PocketMine-MP
