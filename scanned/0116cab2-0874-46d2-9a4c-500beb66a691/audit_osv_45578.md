# [M] sshd in OpenSSH before 10.4 has an undocumented security-relevant behavior:...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1322
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1322
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
sshd in OpenSSH before 10.4 has an undocumented security-relevant behavior: GSSAPIStrictAcceptorCheck has no value if the server is in Windows Active Directory.

## References
- https://github.com/advisories/GHSA-3j2g-cqmq-cjw9
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59998
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
