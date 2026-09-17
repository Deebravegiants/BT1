# [M] JLSEC-2026-34

## Summary
Severity: Medium
Advisory: JLSEC-2026-34
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-34
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
An information leak was discovered in postgresql in versions before 13.2, before 12.6 and before 11.11. A user having UPDATE permission but not SELECT permission to a particular column could craft queries which, under some circumstances, might disclose values from that column in error messages. An attacker could use this flaw to obtain information stored in a column they are allowed to write but not read.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1924005
- https://security.gentoo.org/glsa/202105-32
- https://security.netapp.com/advisory/ntap-20210507-0006/
