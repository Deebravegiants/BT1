# [H] cairo-truetype-subset.c in cairo 1.15.6 and earlier allows remote attackers to cause a denial of...

## Summary
Severity: High
Advisory: JLSEC-2025-12
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-12
Type: osv

## Affected
- Julia: `Cairo_jll` — affected >=0 <1.16.0+0

## Details
cairo-truetype-subset.c in cairo 1.15.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) because of mishandling of an unexpected malloc(0) call.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00042.html
- https://bugs.freedesktop.org/show_bug.cgi?id=101547
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://security.gentoo.org/glsa/201904-01
