# [H] Apache Kyuubi: kyuubi.session.local.dir.allow.list bypass via unprefixed Spark file-conf aliases

## Summary
Severity: High
Advisory: CVE-2026-62391
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-62391
Type: osv

## Details
The security fix for CVE-2025-66518 is incomplete. Any client who can access to Apache Kyuubi Server via Kyuubi frontend protocols can bypass server-side config kyuubi.session.local.dir.allowlist via unprefixed Spark config aliases.

This issue affects Apache Kyuubi: from 1.6.0 before 1.12.0.

Users are recommended to upgrade to version 1.12.0, which fixes the issue.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62391.json
- https://lists.apache.org/thread/vo4k4nxz23kfzrpp120nsojb0vrkx4w1
- https://nvd.nist.gov/vuln/detail/CVE-2026-62391
