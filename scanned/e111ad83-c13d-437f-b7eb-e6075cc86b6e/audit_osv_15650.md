# [M] CVE-2019-18391

## Summary
Severity: Medium
Advisory: CVE-2019-18391
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-18391
Type: osv

## Details
A heap-based buffer overflow in the vrend_renderer_transfer_write_iov function in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service via VIRGL_CCMD_RESOURCE_INLINE_WRITE commands.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00028.html
- https://access.redhat.com/security/cve/cve-2019-18391
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/314/diffs?commit_id=8c9cfb4e425542e96f0717189fe4658555baaf08
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1765589
- https://gitlab.freedesktop.org/virgl/virglrenderer/commit/2abeb1802e3c005b17a7123e382171b3fb665971
