# [H] Apache MINA SSHD bundle sshd-git has a path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-mw4m-qhpg-j82m
CVE: CVE-2026-48827
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-mw4m-qhpg-j82m
Type: github-advisory

## Affected
- Maven: `org.apache.sshd:sshd-git` — affected >=0 <2.18.0
- Maven: `org.apache.sshd:sshd-git` — affected >=3.0.0-M1 <3.0.0-M4

## Details
There is a path traversal vulnerability in Apache MINA SSHD bundle sshd-git. Lack of path validation in git-upload-pack, git-receive-pack, and other git operations allows users authenticated over SSH access to git repositories outside the configured git server root directory.

Applications are affected if they use org.apache.sshd:sshd-git. Applications not using sshd-git are not affected.

Users are advised to upgrade affected applications to Apche MINA SSHD 2.18.0, which fixes the issue.

The issue also is present in the pre-release milestones 3.0.0-M1 to 3.0.0-M3 for a new upcoming new major version 3.0.0. Again, applications are affected only if they use sshd-git. Upgrade affected applications to 3.0.0-M4.

Apache MINA SSHD bundle sshd-git would like to point out that a professional git server should not rely solely on file system layout and permissions, but should implement additional security controls to govern access to git repositories and operations allowed on particular git repositories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48827
- https://github.com/apache/mina-sshd
- https://lists.apache.org/thread/910kq9ghm6js0k1yhhbrdm9sf5tqq9c9
- http://www.openwall.com/lists/oss-security/2026/05/30/1
