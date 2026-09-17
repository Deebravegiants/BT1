# [H] In sshd in OpenSSH before 10.4, DisableForwarding=yes was supposed to take precedence over...

## Summary
Severity: High
Advisory: JLSEC-2026-1323
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1323
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
In sshd in OpenSSH before 10.4, DisableForwarding=yes was supposed to take precedence over PermitTunnel=yes, but did not.

## References
- https://github.com/advisories/GHSA-gcm2-x6hm-q4h3
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59999
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
