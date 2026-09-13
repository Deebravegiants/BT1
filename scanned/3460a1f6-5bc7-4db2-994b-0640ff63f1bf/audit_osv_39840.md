# [H] Spring Data REST allows mutation of identifier and version properties via JSON Patch

## Summary
Severity: High
Advisory: CVE-2026-47849
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-47849
Type: osv

## Details
Spring Data REST does not guard identifier (@Id) and version (@Version) properties against mutation via RFC 6902 JSON Patch (application/json-patch+json) requests.
Spring Data REST 5.1.0
Spring Data REST 5.0.0 - 5.0.6
Spring Data REST 4.5.0 - 4.5.12
Spring Data REST 4.0.0 - 4.4.15
Spring Data REST 3.7.20 and earlier

## References
- https://spring.io/security/cve-2026-47849
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47849.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47849
