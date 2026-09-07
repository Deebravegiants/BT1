# [H] OpenCart Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-v4j2-cwmm-xg89
CVE: CVE-2023-2315
CWE: CWE-20, CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-v4j2-cwmm-xg89
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=4.0.0.0 <4.0.2.3

## Details
Path Traversal in OpenCart versions 4.0.0.0 to 4.0.2.2 allows an authenticated user with access/modify privilege on the Log component to empty out arbitrary files on the server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2315
- https://github.com/opencart/opencart/commit/0a8dd91e385f70e42795380009fd644224c1bc97
- https://github.com/opencart/opencart
- https://github.com/opencart/opencart/releases/tag/4.0.2.3
- https://starlabs.sg/advisories/23/23-2315
