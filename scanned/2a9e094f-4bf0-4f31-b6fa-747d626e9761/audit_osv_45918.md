# [M] JLSEC-2026-474

## Summary
Severity: Medium
Advisory: JLSEC-2026-474
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-474
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.12+0

## Details
A vulnerability was found in libX11 due to an infinite loop within the PutSubImage() function. This flaw allows a local user to consume all available system resources and cause a denial of service condition.

## References
- http://www.openwall.com/lists/oss-security/2024/01/24/9
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43786
- https://bugzilla.redhat.com/show_bug.cgi?id=2242253
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63IBRFLQVZSMOAZBZOBKFWJP26ILRAGQ/
- https://security.netapp.com/advisory/ntap-20231103-0006/
