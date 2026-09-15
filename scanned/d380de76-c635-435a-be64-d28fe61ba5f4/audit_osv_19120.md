# [M] CVE-2020-8002

## Summary
Severity: Medium
Advisory: CVE-2020-8002
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2020-8002
Type: osv

## Details
A NULL pointer dereference in vrend_renderer.c in virglrenderer through 0.8.1 allows attackers to cause a denial of service via commands that attempt to launch a grid without previously providing a Compute Shader (CS).

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00017.html
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340/diffs?commit_id=572a36879701598fa727f50313508be99865b58f
- https://gitlab.freedesktop.org/virgl/virglrenderer/merge_requests/340/diffs?commit_id=725e12beba4a41934f0ab62d399b5d4de2d13190
