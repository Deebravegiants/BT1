# [H] Smarty vulnerable to PHP Code Injection by malicious attribute in extends-tag

## Summary
Severity: High
Advisory: GHSA-4rmg-292m-wg3w
CVE: CVE-2024-35226
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-4rmg-292m-wg3w
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=5.0.0 <5.1.1
- Packagist: `smarty/smarty` — affected >=3.0.0 <4.5.3

## Details
### Impact
Template authors could inject php code by choosing a malicous file name for an extends-tag. Users that cannot fully trust template authors should update asap.

### Patches
Please upgrade to the most recent version of Smarty v4 or v5. There is no patch for v3.

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-4rmg-292m-wg3w
- https://nvd.nist.gov/vuln/detail/CVE-2024-35226
- https://github.com/smarty-php/smarty/commit/0be92bc8a6fb83e6e0d883946f7e7c09ba4e857a
- https://github.com/smarty-php/smarty
- https://lists.debian.org/debian-lts-announce/2024/11/msg00013.html
