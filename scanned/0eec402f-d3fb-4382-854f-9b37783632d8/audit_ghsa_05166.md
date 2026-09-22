# [H] Koillection has an authenticated Server-Side Request Forgery issue

## Summary
Severity: High
Advisory: GHSA-gmxh-hjfv-qc2w
CVE: CVE-2026-50888
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-gmxh-hjfv-qc2w
Type: github-advisory

## Affected
- Packagist: `koillection/koillection` — affected >=0 <1.8.4

## Details
An authenticated Server-Side Request Forgery (SSRF) in the custom scraper subsystem component of Benjamin Jonard Koillection v1.8.0 allows attackers to scan internal resources via supplying a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50888
- https://github.com/benjaminjonard/koillection/pull/1599
- https://github.com/benjaminjonard/koillection/commit/4d445e21c631c26070f19fe8ec086a2939767ae0
- https://gist.github.com/pyuysig/d60273c1c346257ceddbf8da7134bae7
- https://github.com/benjaminjonard/koillection
- https://github.com/benjaminjonard/koillection/releases/tag/1.8.4
