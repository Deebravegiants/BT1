# [M] CVE-2017-5993

## Summary
Severity: Medium
Advisory: CVE-2017-5993
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5993
Type: osv

## Details
Memory leak in the vrend_renderer_init_blit_ctx function in vrend_blitter.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (host memory consumption) via a large number of VIRGL_CCMD_BLIT commands.

## References
- http://www.securityfocus.com/bid/96275
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/15/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1422438
- https://cgit.freedesktop.org/virglrenderer/commit/?id=6eb13f7a2dcf391ec9e19b4c2a79e68305f63c22
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
