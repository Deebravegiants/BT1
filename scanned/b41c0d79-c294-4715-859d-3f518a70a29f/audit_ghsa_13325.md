# [H] Pimcore vulnerable to SQL Injection in Dataobjects sorting

## Summary
Severity: High
Advisory: GHSA-c9hw-557q-f8hq
CVE: CVE-2023-3820
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-c9hw-557q-f8hq
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.6.4

## Details
### Impact
Using some SQL exploitation tools such as sqlmap, an attacker can enumerate all information in the database, alter data or perform dos on the backend database.

### Patches
Update to version 10.6.5 or apply this patch manually https://github.com/pimcore/pimcore/commit/e641968979d4a2377bbea5e2a76bdede040d0b97.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/e641968979d4a2377bbea5e2a76bdede040d0b97.patch manually.

### References
https://huntr.dev/bounties/b00a38b6-d040-494d-bf46-38f46ac1a1db/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-c9hw-557q-f8hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-3820
- https://github.com/pimcore/pimcore/commit/e641968979d4a2377bbea5e2a76bdede040d0b97
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/b00a38b6-d040-494d-bf46-38f46ac1a1db
