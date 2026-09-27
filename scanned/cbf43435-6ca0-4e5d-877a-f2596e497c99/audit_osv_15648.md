# [H] CVE-2019-18389

## Summary
Severity: High
Advisory: CVE-2019-18389
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-18389
Type: osv

## Details
A heap-based buffer overflow in the vrend_renderer_transfer_write_iov function in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service, or QEMU guest-to-host escape and code execution, via VIRGL_CCMD_RESOURCE_INLINE_WRITE commands.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00028.html
- https://access.redhat.com/security/cve/cve-2019-18389
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1765577
- https://gitlab.freedesktop.org/virgl/virglrenderer/commit/cbc8d8b75be360236cada63784046688aeb6d921
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/314/diffs?commit_id=9c280a28651507e6ef87b17b90d47b6af3a4ab7d
