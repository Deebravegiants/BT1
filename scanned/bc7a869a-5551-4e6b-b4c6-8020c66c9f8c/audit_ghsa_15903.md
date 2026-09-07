# [H] Snipe-IT remote code execution

## Summary
Severity: High
Advisory: GHSA-57qh-vmjr-5jxg
CVE: CVE-2024-48987
CWE: CWE-1393
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-57qh-vmjr-5jxg
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <7.0.10

## Details
Snipe-IT before 7.0.10 allows remote code execution (associated with cookie serialization) when an attacker knows the APP_KEY. This is exacerbated by .env files, available from the product's repository, that have default APP_KEY values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48987
- https://github.com/snipe/snipe-it
- https://github.com/snipe/snipe-it/releases/tag/v7.0.10
- https://snipe-it.readme.io/docs/key-rotation
- https://www.synacktiv.com/advisories/snipe-it-unauthenticated-remote-command-execution-when-appkey-known
