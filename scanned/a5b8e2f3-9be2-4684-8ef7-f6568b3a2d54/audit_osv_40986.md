# [H] Apache MINA SSHD: Path traversal in SCP file reception

## Summary
Severity: High
Advisory: CVE-2026-56452
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-56452
Type: osv

## Details
Path traversal in the sshd-scp component of Apache MINA SSHD. Apache MINA SSHD is a Java library for client-side and server-side SSH.




The implementation of receiving files or directories via SCP did not validate filenames in SCP "C" or "D" commands. A malicious sender could send filenames containing paths, resulting in files to be written in attacker-controlled places.




The issue affects only

  *  applications that use no longer supported Apache MINA SSHD versions < 2.0.0 and use the SCP functions to receive files,
  *  or applications using sshd-scp in Apache MINA SSHD >= 2.0.0 to receive files.




Applications using Apache MINA SSHD >= 2.0.0 not using sshd-scp are not affected.




The issue is fixed in Apache MINA 2.19.0 and 3.0.0-M5. Affected applications are advised to upgrade to these versions.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/15
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56452.json
- https://lists.apache.org/thread/xgoqvmksmd94fsqnzqjdtfjxf35os9no
- https://nvd.nist.gov/vuln/detail/CVE-2026-56452
