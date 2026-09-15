# [M] CVE-2017-6386

## Summary
Severity: Medium
Advisory: CVE-2017-6386
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6386
Type: osv

## Details
Memory leak in the vrend_create_vertex_elements_state function in vrend_renderer.c in virglrenderer allows local guest OS users to cause a denial of service (host memory consumption) via a large number of VIRGL_OBJECT_VERTEX_ELEMENTS commands.

## References
- http://www.securityfocus.com/bid/96506
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/03/01/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1427472
- https://cgit.freedesktop.org/virglrenderer/commit/?id=737c3350850ca4dbc5633b3bdb4118176ce59920
