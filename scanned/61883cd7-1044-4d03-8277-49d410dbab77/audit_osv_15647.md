# [M] CVE-2019-18388

## Summary
Severity: Medium
Advisory: CVE-2019-18388
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-18388
Type: osv

## Details
A NULL pointer dereference in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service via malformed commands.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00028.html
- https://access.redhat.com/security/cve/cve-2019-18388
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/314/diffs?commit_id=d2cdbcf6a8f2317f250fd54f08aa35dde2fa3e30#diff-content-3cd772559e0d73afa136d6818023cfd0c4c8ecc0
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1765578
- https://gitlab.freedesktop.org/virgl/virglrenderer/commit/0d9a2c88dc3a70023541b3260b9f00c982abda16
