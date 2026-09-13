# [M] CVE-2017-5937

## Summary
Severity: Medium
Advisory: CVE-2017-5937
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5937
Type: osv

## Details
The util_format_is_pure_uint function in vrend_renderer.c in Virgil 3d project (aka virglrenderer) 0.6.0 and earlier allows local guest OS users to cause a denial of service (NULL pointer dereference) via a crafted VIRGL_CCMD_CLEAR command.

## References
- http://www.securityfocus.com/bid/96180
- http://www.openwall.com/lists/oss-security/2017/02/09/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1420246
- https://cgit.freedesktop.org/virglrenderer/commit/?id=48f67f60967f963b698ec8df57ec6912a43d6282
