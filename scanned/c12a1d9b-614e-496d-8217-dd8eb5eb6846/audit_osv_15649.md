# [H] CVE-2019-18390

## Summary
Severity: High
Advisory: CVE-2019-18390
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-18390
Type: osv

## Details
An out-of-bounds read in the vrend_blit_need_swizzle function in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service via VIRGL_CCMD_BLIT commands.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00028.html
- https://access.redhat.com/security/cve/cve-2019-18390
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/314/diffs?commit_id=d2cdbcf6a8f2317f250fd54f08aa35dde2fa3e30#3cd772559e0d73afa136d6818023cfd0c4c8ecc0_0_151
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1765584
- https://gitlab.freedesktop.org/virgl/virglrenderer/commit/24f67de7a9088a873844a39be03cee6882260ac9
