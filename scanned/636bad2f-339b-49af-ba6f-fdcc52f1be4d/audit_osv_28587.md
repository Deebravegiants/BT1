# [M] Apache Guacamole: Improper input validation of console codes

## Summary
Severity: Medium
Advisory: CVE-2024-35164
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2024-35164
Type: osv

## Details
The terminal emulator of Apache Guacamole 1.5.5 and older does not properly validate console codes received from servers via text-based protocols like SSH. If a malicious user has access to a text-based connection, a specially-crafted sequence of console codes could allow arbitrary code to be executed
with the privileges of the running guacd process.




Users are recommended to upgrade to version 1.6.0, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/01/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35164.json
- https://lists.apache.org/thread/sgs8lplbkrpvd3hrvcnnxh3028h4py70
- https://nvd.nist.gov/vuln/detail/CVE-2024-35164
