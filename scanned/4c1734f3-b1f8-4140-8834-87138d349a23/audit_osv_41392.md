# [M] CVE-2026-59998

## Summary
Severity: Medium
Advisory: CVE-2026-59998
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59998
Type: osv

## Details
sshd in OpenSSH before 10.4 has an undocumented security-relevant behavior: GSSAPIStrictAcceptorCheck has no value if the server is in Windows Active Directory.

## References
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59998
