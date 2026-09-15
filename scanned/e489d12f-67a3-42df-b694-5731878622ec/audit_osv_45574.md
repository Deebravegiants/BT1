# [M] sftp in OpenSSH before 10.4 does not properly constrain the location of downloaded files when ...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1319
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1319
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
sftp in OpenSSH before 10.4 does not properly constrain the location of downloaded files when "sftp server:/path ." is used with an attacker-controlled server.

## References
- https://github.com/advisories/GHSA-2prh-86cw-fm96
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59995
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
