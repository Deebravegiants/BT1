# [M] Craftql vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-8wmw-prw8-2ggm
CVE: CVE-2026-31317
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-8wmw-prw8-2ggm
Type: github-advisory

## Affected
- Packagist: `markhuot/craftql` — affected >=0

## Details
Craftql v1.3.7 and before is vulnerable to Server-Side Request Forgery (SSRF) which allows an attacker to execute arbitrary code via the vendor/markhuot/craftql/src/Listeners/GetAssetsFieldSchema.php file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31317
- https://github.com/markhuot/craftql
- https://github.com/stormmmg/craftql_ssrf
- https://github.com/stormmmg/craftql_ssrf/blob/master/craftql-ssrf-en/README_detail.md
