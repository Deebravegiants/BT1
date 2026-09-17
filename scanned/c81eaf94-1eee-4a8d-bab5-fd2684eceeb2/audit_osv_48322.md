# [M] CVE-2017-6355

## Summary
Severity: Medium
Advisory: CVE-2017-6355
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6355
Type: osv

## Details
Integer overflow in the vrend_create_shader function in vrend_renderer.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (process crash) via crafted pkt_length and offlen values, which trigger an out-of-bounds access.

## References
- http://www.securityfocus.com/bid/96460
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/27/3
- https://cgit.freedesktop.org/virglrenderer/commit/?id=93761787b29f37fa627dea9082cdfc1a1ec608d6
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
