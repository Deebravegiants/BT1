# [H] Weblate has an arbitrary file read via symbolic links

## Summary
Severity: High
Advisory: GHSA-g925-f788-4jh7
CVE: CVE-2025-68279
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-g925-f788-4jh7
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.15.1

## Details
### Impact
It was possible to read arbitrary files from the server file system using crafted symbolic links in the repository.

### Resources

Thanks to Jason Marcello for responsible disclosure.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-g925-f788-4jh7
- https://nvd.nist.gov/vuln/detail/CVE-2025-68279
- https://github.com/WeblateOrg/weblate/pull/17331
- https://github.com/WeblateOrg/weblate/pull/17356
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.15.1
