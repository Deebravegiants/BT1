# [M] A stack buffer overflow flaw was found in Libtiffs' tiffcp.c in main() function

## Summary
Severity: Medium
Advisory: JLSEC-2025-281
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-281
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.4.0+0

## Details
A stack buffer overflow flaw was found in Libtiffs' tiffcp.c in main() function. This flaw allows an attacker to pass a crafted TIFF file to the tiffcp tool, triggering a stack buffer overflow issue, possibly corrupting the memory, and causing a crash that leads to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-1355
- https://bugzilla.redhat.com/show_bug.cgi?id=2074415
- https://gitlab.com/libtiff/libtiff/-/issues/400
- https://gitlab.com/libtiff/libtiff/-/merge_requests/323
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221014-0007/
- https://www.debian.org/security/2023/dsa-5333
