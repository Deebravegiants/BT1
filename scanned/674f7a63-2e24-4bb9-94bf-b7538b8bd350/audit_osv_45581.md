# [C] ssh in OpenSSH before 10.4 can have a use-after-free when a server changes its host key during a...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1326
Ecosystem: Julia
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1326
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
ssh in OpenSSH before 10.4 can have a use-after-free when a server changes its host key during a key re-exchange. (This outcome occurs only on the client side.)

## References
- https://github.com/advisories/GHSA-gp5v-jg37-fvg6
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-60002
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
