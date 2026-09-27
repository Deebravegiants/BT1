# [M] CVE-2026-59997

## Summary
Severity: Medium
Advisory: CVE-2026-59997
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59997
Type: osv

## Details
internal-sftp in sshd in OpenSSH before 10.4 recognizes only the first 9 command-line arguments, which can be important if a later command-line argument would have helped to ensure the intended security properties of an SFTP connection.

## References
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59997.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59997
