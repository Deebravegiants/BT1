# [M] Self Routing guard bypassed via function composition

## Summary
Severity: Medium
Advisory: CVE-2026-40989
Aliases: GHSA-x9c7-5h6g-hq8q
CVSS: 5.7 (CVSS:3.1/AV:P/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-40989
Type: osv

## Details
Under infinite recursion in the routing layer, request-handling can cause OOM error.

Affected Spring Products and Versions:
Spring Cloud Function 3.2.x: versions prior to 3.2.16
Spring Cloud Function 4.1.x: versions prior to 4.1.10
Spring Cloud Function 4.2.x: versions prior to 4.2.6
Spring Cloud Function 4.3.x: versions prior to 4.3.3
Spring Cloud Function 5.0.x: versions prior to 5.0.2
Older, unsupported versions are also affected.

## References
- https://spring.io/security/cve-2026-40989
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40989.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40989
