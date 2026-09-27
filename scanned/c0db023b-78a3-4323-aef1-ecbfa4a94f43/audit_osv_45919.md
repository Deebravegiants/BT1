# [H] JLSEC-2026-475

## Summary
Severity: High
Advisory: JLSEC-2026-475
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-475
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.12+0

## Details
A vulnerability was found in libX11 due to an integer overflow within the XCreateImage() function. This flaw allows a local user to trigger an integer overflow and execute arbitrary code with elevated privileges.

## References
- http://www.openwall.com/lists/oss-security/2024/01/24/9
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43787
- https://bugzilla.redhat.com/show_bug.cgi?id=2242254
- https://jfrog.com/blog/xorg-libx11-vulns-cve-2023-43786-cve-2023-43787-part-two/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://security.netapp.com/advisory/ntap-20231103-0006/
