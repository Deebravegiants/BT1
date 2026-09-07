# [M] Snipe-IT allows stored XSS via the Locations "Country" field

## Summary
Severity: Medium
Advisory: GHSA-4g25-wj72-chxg
CVE: CVE-2025-65622
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-4g25-wj72-chxg
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.3.4

## Details
Snipe-IT before 8.3.4 allows stored XSS via the Locations "Country" field, enabling a low-privileged authenticated user to inject JavaScript that executes in another user's session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65622
- https://github.com/grokability/snipe-it/commit/23feb64b5ab3d92eb8755da41049ac43a3d0e05b
- https://github.com/firef0x00/vulnerability-research/tree/main/CVE-2025-65622
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.3.4
- http://snipeitapp.com
