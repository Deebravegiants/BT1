# [M] CVE-2020-8003

## Summary
Severity: Medium
Advisory: CVE-2020-8003
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2020-8003
Type: osv

## Details
A double-free vulnerability in vrend_renderer.c in virglrenderer through 0.8.1 allows attackers to cause a denial of service by triggering texture allocation failure, because vrend_renderer_resource_allocated_texture is not an appropriate place for a free.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://gitlab.freedesktop.org/virgl/virglrenderer/commit/f9b079ccc319c98499111f66bd654fc9b56cf15f?merge_request_iid=340
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340/diffs?commit_id=3320973c9f2068f60cf6613c2811a8824781878a
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340/diffs?commit_id=f9b079ccc319c98499111f66bd654fc9b56cf15f
