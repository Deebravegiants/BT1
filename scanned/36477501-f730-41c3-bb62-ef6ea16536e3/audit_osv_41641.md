# [M] Apache Accumulo: A user can trigger a graceful shutdown of services without the relevant system permissions

## Summary
Severity: Medium
Advisory: CVE-2026-62764
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/S:N/AU:Y/R:U/V:D/RE:L/U:Green)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62764
Type: osv

## Details
Improper Handling of Insufficient Privileges vulnerability in Apache Accumulo.
An authenticated, but low-privileged user without system permissions may
issue a remote command to gracefully shutdown system components
(compaction-coordinator, compactor, gc, manager, monitor, tserver, or sserver),
leading to a denial of service.

This issue affects Apache Accumulo 2.1.4 and 2.1.5.

Users are recommended to upgrade to version 2.1.6, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/6
- https://repo.maven.apache.org/maven2
- https://accumulo.apache.org/release/accumulo-2.1.6/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62764.json
- https://lists.apache.org/thread/qclg736k93oqn4qrpw9wxjbb3jhn6gm1
- https://nvd.nist.gov/vuln/detail/CVE-2026-62764
- https://github.com/apache/accumulo/issues/6478
- https://accumulo.apache.org/downloads/
