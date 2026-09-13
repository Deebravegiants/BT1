# [H] JLSEC-2026-31

## Summary
Severity: High
Advisory: JLSEC-2026-31
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-31
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A flaw was found in postgresql in versions before 13.3, before 12.7, before 11.12, before 10.17 and before 9.6.22. While modifying certain SQL array values, missing bounds checks let authenticated database users write arbitrary bytes to a wide area of server memory. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1956876
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20210713-0004/
- https://www.postgresql.org/support/security/CVE-2021-32027/
