# [M] CVE-2017-6210

## Summary
Severity: Medium
Advisory: CVE-2017-6210
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6210
Type: osv

## Details
The vrend_decode_reset function in vrend_decode.c in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (NULL pointer dereference and QEMU process crash) by destroying context 0 (zero).

## References
- http://www.securityfocus.com/bid/96439
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/23/21
- https://bugzilla.redhat.com/show_bug.cgi?id=1426170
- https://cgit.freedesktop.org/virglrenderer/commit/?id=0a5dff15912207b83018485f83e067474e818bab
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
