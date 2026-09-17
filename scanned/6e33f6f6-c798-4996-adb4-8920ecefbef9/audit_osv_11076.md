# [M] CVE-2017-5956

## Summary
Severity: Medium
Advisory: CVE-2017-5956
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-5956
Type: osv

## Details
The vrend_draw_vbo function in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (out-of-bounds array access and QEMU process crash) via vectors involving vertext_buffer_index.

## References
- http://www.securityfocus.com/bid/96187
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/13/2
- https://cgit.freedesktop.org/virglrenderer/commit/?id=a5ac49940c40ae415eac0cf912eac7070b4ba95d
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
