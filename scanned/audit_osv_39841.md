# [M] Spring Data REST allows mutation of the version property of immutable aggregates via PUT

## Summary
Severity: Medium
Advisory: CVE-2026-47850
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47850
Type: osv

## Details
Spring Data REST does not preserve the persisted version (@Version) property of an aggregate root when handling an HTTP PUT against an immutable target type.
Spring Data REST 5.1.0
Spring Data REST 5.0.0 - 5.0.6
Spring Data REST 4.5.0 - 4.5.12
Spring Data REST 4.0.0 - 4.4.15
Spring Data REST 3.7.20 and earlier

## References
- https://spring.io/security/cve-2026-47850
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47850.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47850
