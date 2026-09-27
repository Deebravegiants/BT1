# [H] Apache Qpid Proton-J: Unbounded type nesting can lead to pre-authentication stackoverflow

## Summary
Severity: High
Advisory: CVE-2026-66274
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-66274
Type: osv

## Details
A pre-authentication attacker could leverage type nesting to cause a StackOverflowError potentially leading to denial of service.

This issue affects Apache Qpid Proton-J: through 0.34.1.

Users are recommended to upgrade to version 0.35.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/10
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66274.json
- https://lists.apache.org/thread/h7xolzws2by2qhdjf7scbx87foxojb5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-66274
