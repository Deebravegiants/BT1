# [H] JLSEC-2026-78

## Summary
Severity: High
Advisory: JLSEC-2026-78
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-78
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.3.1+0

## Details
OpenSSH before 10.3 mishandles the `authorized_keys` principals option in uncommon scenarios involving a principals list in conjunction with a Certificate Authority that makes certain use of comma characters.

## References
- https://marc.info/?l=openssh-unix-dev&m=177513443901484&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35414
- https://www.openssh.org/releasenotes.html#10.3p1
- https://www.openwall.com/lists/oss-security/2026/04/02/3
