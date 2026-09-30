# [M] CVE-2017-5957

## Summary
Severity: Medium
Advisory: CVE-2017-5957
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2017-5957
Type: osv

## Details
Stack-based buffer overflow in the vrend_decode_set_framebuffer_state function in vrend_decode.c in virglrenderer before 926b9b3460a48f6454d8bbe9e44313d86a65447f, as used in Quick Emulator (QEMU), allows a local guest users to cause a denial of service (application crash) via the "nr_cbufs" argument.

## References
- http://www.securityfocus.com/bid/96215
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/13/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1421126
- https://cgit.freedesktop.org/virglrenderer/commit/?id=926b9b3460a48f6454d8bbe9e44313d86a65447f
