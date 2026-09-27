# [H] Apache MINA SSHD: Path traversal in org.apache.sshd:sshd-git on Windows

## Summary
Severity: High
Advisory: CVE-2026-56623
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-56623
Type: osv

## Details
Path traversal on Windows in Apache MINA SSHD component sshd-git. Apache MINA SSHD is a Java library for client-side and server-side SSH.




A git server implemented with Apache MINA SSHD component sshd-git and running on Windows could allow an authenticated remote user access to git repositories outside of the configured server-side root directory. The path validation applied for CVE-2026-48827 in Apache MINA SSHD 2.18.0 and 3.0.0-M4 was partly ineffective for Servers running on Windows.




Applications are affected if they use org.apache.sshd:sshd-git to implement a git server and run on Windows. Applications not using sshd-git or not running on Windows are not affected.




Users are advised to upgrade affected applications to Apache MINA SSHD 2.19.0, which fixes the issue.




The issue also is present in the pre-release milestones 3.0.0-M1 to 3.0.0-M4 for a new upcoming new major version 3.0.0. Again, applications are affected only if they use sshd-git and run on Windows. Upgrade affected applications to 3.0.0-M5.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56623.json
- https://lists.apache.org/thread/bhw26snzgvk0mtqqp5dcyjvczp4kcqky
- https://nvd.nist.gov/vuln/detail/CVE-2026-56623
