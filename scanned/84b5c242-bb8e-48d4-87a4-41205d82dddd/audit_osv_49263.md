# [M] CVE-2018-7731

## Summary
Severity: Medium
Advisory: CVE-2018-7731
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7731
Type: osv

## Details
An issue was discovered in Exempi through 2.4.4. XMPFiles/source/FormatSupport/WEBP_Support.cpp does not check whether a bitstream has a NULL value, leading to a NULL pointer dereference in the WEBP::VP8XChunk class.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BCFXKOOATZ2B5G3G7EBXZWVZHEABN4ZV/
- https://usn.ubuntu.com/3668-1/
- https://bugs.freedesktop.org/show_bug.cgi?id=105247
- https://cgit.freedesktop.org/exempi/commit/?id=aabedb5e749dd59112a3fe1e8e08f2d934f56666
