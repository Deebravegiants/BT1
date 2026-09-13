# [M] CVE-2017-6209

## Summary
Severity: Medium
Advisory: CVE-2017-6209
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6209
Type: osv

## Details
Stack-based buffer overflow in the parse_identifier function in tgsi_text.c in the TGSI auxiliary module in the Gallium driver in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (out-of-bounds array access and QEMU process crash) via vectors related to parsing properties.

## References
- http://www.securityfocus.com/bid/96437
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/23/20
- https://bugzilla.redhat.com/show_bug.cgi?id=1426149
- https://cgit.freedesktop.org/virglrenderer/commit/?id=e534b51ca3c3cd25f3990589932a9ed711c59b27
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
