# [M] pimcore is vulnerable to cross-site scripting in Composite indices key field

## Summary
Severity: Medium
Advisory: GHSA-4f25-2x2c-vg6v
CVE: CVE-2023-1703
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-4f25-2x2c-vg6v
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.20

## Details
### Impact
Pimcore is vulnerable to Cross site scripting vulnerability in classes module.

### Patches
Update to version 10.5.20.

### Workarounds
Apply the patch https://github.com/pimcore/pimcore/commit/765832f0dc5f6cfb296a82e089b701066f27bcef.patch manually.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-4f25-2x2c-vg6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-1703
- https://github.com/pimcore/pimcore/commit/765832f0dc5f6cfb296a82e089b701066f27bcef
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/d12d105c-18fa-4d08-b591-b0e89e39eec1
