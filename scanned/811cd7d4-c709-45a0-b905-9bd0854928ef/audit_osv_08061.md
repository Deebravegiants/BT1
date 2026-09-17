# [M] CVE-2016-10163

## Summary
Severity: Medium
Advisory: CVE-2016-10163
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10163
Type: osv

## Details
Memory leak in the vrend_renderer_context_create_internal function in vrend_decode.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (host memory consumption) by repeatedly creating a decode context.

## References
- http://www.securityfocus.com/bid/95784
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/01/24/2
- http://www.openwall.com/lists/oss-security/2017/01/25/4
- https://cgit.freedesktop.org/virglrenderer/commit/?id=747a293ff6055203e529f083896b823e22523fe7
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
