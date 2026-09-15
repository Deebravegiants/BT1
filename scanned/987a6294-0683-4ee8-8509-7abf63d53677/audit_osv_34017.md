# [M] Apache Gravitino: SQL misconfiguration can access or truncate files

## Summary
Severity: Medium
Advisory: CVE-2025-53648
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-53648
Type: osv

## Details
SQL misconfiguration in the Gravitino UI, in versions 1.0.0 and below, can allow a malicious user to read or truncate files.
Users are recommended to upgrade to version 1.0.0, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/30/2
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53648.json
- https://lists.apache.org/thread/s0hytcv17z52dwp5dojjjwgrtqtyh2xk
- https://nvd.nist.gov/vuln/detail/CVE-2025-53648
