# [M] Apache Qpid Broker-J: Unbounded echo flow responses can lead to denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-68080
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-68080
Type: osv

## Details
It was not possible to govern the rate at which the broker would respond to an echo flow, enabling an authenticated attacker to cause excessive resource usage and potential denial of service.

This issue affects Apache Qpid Broker-J: through 10.0.1.

Users are recommended to upgrade to version 10.1.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/20
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68080.json
- https://lists.apache.org/thread/tcnrv5nhmnsrzz92o4owxgycro6llt57
- https://nvd.nist.gov/vuln/detail/CVE-2026-68080
