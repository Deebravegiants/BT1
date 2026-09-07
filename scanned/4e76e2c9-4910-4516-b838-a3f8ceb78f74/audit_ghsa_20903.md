# [C] ThinkPHP deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qjjj-7g7h-54v3
CVE: CVE-2022-38352
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-qjjj-7g7h-54v3
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
ThinkPHP v6.0.13 was discovered to contain a deserialization vulnerability via the component `League\Flysystem\Cached\Storage\Psr6Cache`. This vulnerability allows attackers to execute arbitrary code via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38352
- https://github.com/top-think/framework/issues/2749
- https://github.com/top-think/framework
