# [M] CVE-2017-6317

## Summary
Severity: Medium
Advisory: CVE-2017-6317
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6317
Type: osv

## Details
Memory leak in the add_shader_program function in vrend_renderer.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (host memory consumption) via vectors involving the sprog variable.

## References
- http://www.securityfocus.com/bid/96450
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/24/5
- https://bugzilla.redhat.com/show_bug.cgi?id=1426756
- https://cgit.freedesktop.org/virglrenderer/commit/?id=a2f12a1b0f95b13b6f8dc3d05d7b74b4386394e4
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
