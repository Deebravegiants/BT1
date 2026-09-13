# [M] JLSEC-2026-473

## Summary
Severity: Medium
Advisory: JLSEC-2026-473
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-473
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.12+0

## Details
A vulnerability was found in libX11 due to a boundary condition within the `_XkbReadKeySyms()` function. This flaw allows a local user to trigger an out-of-bounds read error and read the contents of memory on the system.

## References
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43785
- https://bugzilla.redhat.com/show_bug.cgi?id=2242252
- https://lists.debian.org/debian-lts-announce/2023/10/msg00004.html
- https://security.netapp.com/advisory/ntap-20231103-0006/
