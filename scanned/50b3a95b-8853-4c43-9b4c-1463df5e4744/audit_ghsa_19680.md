# [H] Apache Commons VFS Has Relative Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-9q4x-fr4m-jp86
CVE: CVE-2025-27553
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-23
Source: https://github.com/advisories/GHSA-9q4x-fr4m-jp86
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-vfs2` — affected >=0 <2.10.0

## Details
Relative Path Traversal vulnerability in Apache Commons VFS before 2.10.0.

The FileObject API in Commons VFS has a 'resolveFile' method that
takes a 'scope' parameter. Specifying 'NameScope.DESCENDENT' promises that "an exception is thrown if the resolved file is not a descendent of
the base file". However, when the path contains encoded ".."
characters (for example, "%2E%2E/bar.txt"), it might return file objects that are not
a descendent of the base file, without throwing an exception.
This issue affects Apache Commons VFS: before 2.10.0.

Users are recommended to upgrade to version 2.10.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27553
- https://github.com/apache/commons-vfs
- https://lists.apache.org/thread/cnzqowyw9r2pl263cylmxhnvh41hyjcb
- https://lists.debian.org/debian-lts-announce/2025/04/msg00006.html
- http://www.openwall.com/lists/oss-security/2025/03/23/1
