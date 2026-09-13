# [H] JLSEC-2026-25

## Summary
Severity: High
Advisory: JLSEC-2026-25
Ecosystem: Julia
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-25
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
It was found that some PostgreSQL extensions did not use `search_path` safely in their installation script. An attacker with sufficient privileges could use this flaw to trick an administrator into executing a specially crafted script, during the installation or update of such extension. This affects PostgreSQL versions before 12.4, before 11.9, before 10.14, before 9.6.19, and before 9.5.23.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00043.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00008.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1865746
- https://lists.debian.org/debian-lts-announce/2020/08/msg00028.html
- https://security.gentoo.org/glsa/202008-13
- https://security.netapp.com/advisory/ntap-20200918-0002/
- https://usn.ubuntu.com/4472-1/
