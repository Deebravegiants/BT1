# [H] ALPINE-CVE-2019-18389

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18389
Ecosystem: Alpine:v3.11
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18389
Type: osv

## Affected
- Alpine:v3.11: `virglrenderer` — affected >=0 <0.8.1-r0

## Details
A heap-based buffer overflow in the vrend_renderer_transfer_write_iov function in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service, or QEMU guest-to-host escape and code execution, via VIRGL_CCMD_RESOURCE_INLINE_WRITE commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18389
