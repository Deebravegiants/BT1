# [M] XBlock custom auth does not respect JWT Scopes

## Summary
Severity: Medium
Advisory: CVE-2024-22209
Aliases: GHSA-qx8m-mqx3-j9fm
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2024-01-13
Source: https://osv.dev/vulnerability/CVE-2024-22209
Type: osv

## Details
Open edX Platform is a service-oriented platform for authoring and delivering online learning. A user with a JWT and more limited scopes could call endpoints exceeding their access. This vulnerability has been patched in commit 019888f.

## References
- https://github.com/openedx/edx-platform/blob/0b3e4d73b6fb6f41ae87cf2b77bca12052ee1ac8/lms/djangoapps/courseware/block_render.py#L752-L775
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22209.json
- https://github.com/openedx/edx-platform/security/advisories/GHSA-qx8m-mqx3-j9fm
- https://nvd.nist.gov/vuln/detail/CVE-2024-22209
- https://github.com/openedx/edx-platform/commit/019888f3d15beaebcb7782934f6c43b0c2b3735e
