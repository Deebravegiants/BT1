# [M] ALPINE-CVE-2019-18388

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-18388
Ecosystem: Alpine:v3.11
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18388
Type: osv

## Affected
- Alpine:v3.11: `virglrenderer` — affected >=0 <0.8.1-r0

## Details
A NULL pointer dereference in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service via malformed commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18388
