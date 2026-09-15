# [M] JLSEC-2026-32

## Summary
Severity: Medium
Advisory: JLSEC-2026-32
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-32
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A flaw was found in postgresql. Using an INSERT ... ON CONFLICT ... DO UPDATE command on a purpose-crafted table, an authenticated database user could read arbitrary bytes of server memory. The highest threat from this vulnerability is to data confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1956877
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20211112-0003/
- https://www.postgresql.org/support/security/CVE-2021-32028
