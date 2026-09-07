# [H] Pimcore vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-r87r-982q-2c3q
CVE: CVE-2023-3819
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-r87r-982q-2c3q
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.6.4

## Details
### Impact
Unauthorized users are able to obtain sensitive information about the system's runtime environment, features they have no permissions to access, etc.

### Patches
Update to version 10.6.4 or apply this patch manually https://github.com/pimcore/pimcore/commit/0237527b3244d251fa5ecd4912dfe4f8b2125c54.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/0237527b3244d251fa5ecd4912dfe4f8b2125c54.patch manually.

### References
https://huntr.dev/bounties/be5e4d4c-1b0b-4c01-a1fc-00533135817c/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-r87r-982q-2c3q
- https://nvd.nist.gov/vuln/detail/CVE-2023-3819
- https://github.com/pimcore/pimcore/commit/0237527b3244d251fa5ecd4912dfe4f8b2125c54
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/be5e4d4c-1b0b-4c01-a1fc-00533135817c
