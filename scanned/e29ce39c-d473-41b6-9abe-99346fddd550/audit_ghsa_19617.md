# [M] Apache Commons VFS Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-3936-3gx6-49c4
CVE: CVE-2025-30474
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-23
Source: https://github.com/advisories/GHSA-3936-3gx6-49c4
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-vfs2` — affected >=0 <2.10.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Commons VFS.

The FtpFileObject class can throw an exception when a file is not found, revealing the original URI in its message, which may include a password. The fix is to mask the password in the exception message
This issue affects Apache Commons VFS: before 2.10.0.

Users are recommended to upgrade to version 2.10.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30474
- https://github.com/apache/commons-vfs
- https://issues.apache.org/jira/browse/VFS-169
- https://lists.apache.org/thread/w6ztgnbk6ccry3470x191g3xwrpgy6f4
- http://www.openwall.com/lists/oss-security/2025/03/23/2
