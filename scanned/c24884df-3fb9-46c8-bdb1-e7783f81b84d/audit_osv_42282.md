# [M] Apache Qpid Proton-J: Incoming session flow control window can be exceeded

## Summary
Severity: Medium
Advisory: CVE-2026-66275
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-66275
Type: osv

## Details
An authenticated attacker could exceed the session flow control incoming window potentially leading to denial of service.

This issue affects Apache Qpid Proton-J: through 0.34.1.

Users are recommended to upgrade to version 0.35.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/11
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66275.json
- https://lists.apache.org/thread/jds59nxrgcxtlx7xl0kvl5hqt07thxzt
- https://nvd.nist.gov/vuln/detail/CVE-2026-66275
