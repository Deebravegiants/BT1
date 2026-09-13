# [M] JLSEC-2026-286

## Summary
Severity: Medium
Advisory: JLSEC-2026-286
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/JLSEC-2026-286
Type: osv

## Affected
- Julia: `Xorg_libXpm_jll` — affected >=0 <3.5.17+0

## Details
A vulnerability was found in libXpm due to a boundary condition within the XpmCreateXpmImageFromBuffer() function. This flaw allows a local attacker to trigger an out-of-bounds read error and read the contents of memory on the system.

## References
- https://access.redhat.com/errata/RHSA-2024:2146
- https://access.redhat.com/errata/RHSA-2024:2217
- https://access.redhat.com/errata/RHSA-2024:2974
- https://access.redhat.com/errata/RHSA-2024:3022
- https://access.redhat.com/security/cve/CVE-2023-43788
- https://bugzilla.redhat.com/show_bug.cgi?id=2242248
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63IBRFLQVZSMOAZBZOBKFWJP26ILRAGQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I3KFUQT42R7TB4D7RISNSBQFJGLTQGUL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TFAJTBNO3PAIA6EGZR4PN62H6RLKNDTE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V6FARGWN7VWXXWPXYNEEDJLRR3EWFZ3T/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZECBCLDYUGLDSVV75ECPIBW7JXOB3747/
