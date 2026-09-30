# [M] CVE-2017-5994

## Summary
Severity: Medium
Advisory: CVE-2017-5994
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5994
Type: osv

## Details
Heap-based buffer overflow in the vrend_create_vertex_elements_state function in vrend_renderer.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (out-of-bounds array access and crash) via the num_elements parameter.

## References
- http://www.securityfocus.com/bid/96276
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/15/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1422452
- https://cgit.freedesktop.org/virglrenderer/commit/?id=114688c526fe45f341d75ccd1d85473c3b08f7a7
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
