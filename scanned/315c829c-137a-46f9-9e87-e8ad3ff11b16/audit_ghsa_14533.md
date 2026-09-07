# [M] Pimcore vulnerable to Cross Site Scripting in Documents Link Editable

## Summary
Severity: Medium
Advisory: GHSA-97cp-8873-v2gf
CVE: CVE-2023-1115
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-97cp-8873-v2gf
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.18

## Details
### Impact
An attacker can use XSS to send a malicious script to any user through Document Page Link Editable -> Advanced -> Attributes

### Patches
Update to version 10.5.18 or apply this patch manually https://github.com/pimcore/pimcore/pull/14500.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14500.patch manually.

### References
https://huntr.dev/bounties/cfa80332-e4cf-4d64-b3e5-e10298628d17/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-97cp-8873-v2gf
- https://nvd.nist.gov/vuln/detail/CVE-2023-1115
- https://github.com/pimcore/pimcore/pull/14500.patch
- https://github.com/pimcore/pimcore/commit/c6368b7cc69a3ebf2c83de7586f492ca1f404dd3
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/cfa80332-e4cf-4d64-b3e5-e10298628d17
