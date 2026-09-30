# [C] Islandora 2.0 before 2.4.1 could allow any user to upload content into a repository

## Summary
Severity: Critical
Advisory: GHSA-m58q-qq5h-mgqq
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-21
Source: https://github.com/advisories/GHSA-m58q-qq5h-mgqq
Type: github-advisory

## Affected
- Packagist: `islandora/islandora` — affected >=2.0 <2.4.1

## Details
### Impact
This vulnerability would allow any user, regardless of permissions, to upload content into a repository. This affects installations of Islandora core 2.0 or greater.

### Patches
Upgrade immediately to the [latest release](https://github.com/Islandora/islandora/releases/tag/2.4.1) of Islandora.

### Workarounds
In lieu of an upgrade the [following module](https://github.com/Islandora/islandora_ghsa_route_fix) can be leveraged that will resolve the issue until such a time an upgrade can take place.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Islandora](https://github.com/Islandora/islandora)
* Contact community@islandora.ca.

## References
- https://github.com/Islandora/islandora/security/advisories/GHSA-m58q-qq5h-mgqq
- https://github.com/Islandora/islandora/commit/573d6878edf057987f1e41e5068de0074573e4c7
- https://github.com/Islandora-CLAW/islandora
- https://github.com/Islandora/islandora/releases/tag/2.4.1
