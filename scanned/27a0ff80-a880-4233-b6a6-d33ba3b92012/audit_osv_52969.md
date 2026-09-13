# [H] CVE-2022-2319

## Summary
Severity: High
Advisory: CVE-2022-2319
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-2319
Type: osv

## Details
A flaw was found in the Xorg-x11-server. An out-of-bounds access issue can occur in the ProcXkbSetGeometry function due to improper validation of the request length.

## References
- https://security.gentoo.org/glsa/202210-30
- https://security.netapp.com/advisory/ntap-20221104-0003/
- https://www.zerodayinitiative.com/advisories/ZDI-22-964/
- https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/938
- https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/939
- https://lists.freedesktop.org/archives/xorg-announce/2022-July/003192.html
