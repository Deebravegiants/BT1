# [H] SQL Injection in AssetController

## Summary
Severity: High
Advisory: GHSA-4x35-vr82-xvj6
CVE: CVE-2023-2338
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-4x35-vr82-xvj6
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
SQL injections in AssetController due to unsanitized concatenating strings in where clause. The attacker can dump database, alter data or perform dos on the backend database.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/21e35af721c375ef4676ed50835e30d828e76520.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/21e35af721c375ef4676ed50835e30d828e76520.patch manually.

### References
https://huntr.dev/bounties/bbf59fa7-cf5b-4945-81b0-328adc710462/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-4x35-vr82-xvj6
- https://nvd.nist.gov/vuln/detail/CVE-2023-2338
- https://github.com/pimcore/pimcore/commit/21e35af721c375ef4676ed50835e30d828e76520
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/bbf59fa7-cf5b-4945-81b0-328adc710462
