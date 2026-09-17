# [M] Apache Gravitino: Authenticated SSRF in Gravitino JobManager allows server-side HTTP requests to internal network and cloud metadata endpoints via unvalidated job template URIs

## Summary
Severity: Medium
Advisory: CVE-2026-49876
Aliases: PYSEC-2026-3442
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-49876
Type: osv

## Details
Authenticated SSRF in Gravitino JobManager allows server-side HTTP requests to internal network and cloud metadata endpoints via unvalidated job template URIs. A vulnerability in Apache Gravitino.

This issue affects Apache Gravitino: from 1.0.0 through 1.2.1.

Users are recommended to upgrade to version 1.3.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/2
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49876.json
- https://lists.apache.org/thread/2ffkj771d6dp1okh2cdtody969hoo1zs
- https://nvd.nist.gov/vuln/detail/CVE-2026-49876
