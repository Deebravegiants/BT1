# [C] Deserialization of Untrusted Data in topthink/framework

## Summary
Severity: Critical
Advisory: GHSA-qrvj-274h-hfcg
CVE: CVE-2021-36567
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-07
Source: https://github.com/advisories/GHSA-qrvj-274h-hfcg
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
ThinkPHP v6.0.8 was discovered to contain a deserialization vulnerability via the component League\Flysystem\Cached\Storage\AbstractCache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36567
- https://github.com/top-think/framework/issues/2561
- https://github.com/top-think/framework
