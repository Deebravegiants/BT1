# [M] Cross-site Scripting (XSS) in DataObject columns grid

## Summary
Severity: Medium
Advisory: GHSA-g93x-fm2w-5pxw
CVE: CVE-2023-2340
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-g93x-fm2w-5pxw
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
The attacker is capable to stolen the user session cookie. it will leads to complete account takeover.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/aa38319e353cc3cdfac12e03e21ed7a8f3628d3e.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/aa38319e353cc3cdfac12e03e21ed7a8f3628d3e.patch manually.

### References
https://huntr.dev/bounties/964762b0-b4fe-441c-81e1-0ebdbbf80f3b/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-g93x-fm2w-5pxw
- https://nvd.nist.gov/vuln/detail/CVE-2023-2340
- https://github.com/pimcore/pimcore/commit/aa38319e353cc3cdfac12e03e21ed7a8f3628d3e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/964762b0-b4fe-441c-81e1-0ebdbbf80f3b
