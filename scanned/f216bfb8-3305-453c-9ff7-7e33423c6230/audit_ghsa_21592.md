# [H] Cross-site Scripting in Apache Hama

## Summary
Severity: High
Advisory: GHSA-4wfh-48v4-3r84
CVE: CVE-2022-45470
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-4wfh-48v4-3r84
Type: github-advisory

## Affected
- Maven: `org.apache.hama:hama-core` — affected >=0

## Details
Missing input validation in Apache Hama may cause information disclosure through path traversal and XSS. Since Apache Hama is EOL, we do not expect these issues to be fixed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45470
- https://lists.apache.org/thread/ztvoshd4kxvp5vlro52mpgpfxct4ft8l
- http://www.openwall.com/lists/oss-security/2022/11/21/1
