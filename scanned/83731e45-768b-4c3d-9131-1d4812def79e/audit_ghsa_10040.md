# [M] Weblate: Authenticated SSRF via redirect bypass of ALLOWED_ASSET_DOMAINS in screenshot URL uploads

## Summary
Severity: Medium
Advisory: GHSA-5fhx-9jwj-867m
CVE: CVE-2026-33440
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-5fhx-9jwj-867m
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17

## Details
### Impact
The ALLOWED_ASSET_DOMAINS setting applied only to the first issued requests and didn't restrict possible redirects.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18550

### References
This issue was reported by @spbavarva via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-5fhx-9jwj-867m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33440
- https://github.com/WeblateOrg/weblate/pull/18550
- https://github.com/WeblateOrg/weblate/commit/8be80625a864c8db5854503872a65e8a0b7399a6
- https://github.com/WeblateOrg/weblate
