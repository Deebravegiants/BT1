# [M] internal-sftp in sshd in OpenSSH before 10.4 recognizes only the first 9 command-line arguments,...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1321
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1321
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
internal-sftp in sshd in OpenSSH before 10.4 recognizes only the first 9 command-line arguments, which can be important if a later command-line argument would have helped to ensure the intended security properties of an SFTP connection.

## References
- https://github.com/advisories/GHSA-56r6-6mmg-25j5
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59997
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
