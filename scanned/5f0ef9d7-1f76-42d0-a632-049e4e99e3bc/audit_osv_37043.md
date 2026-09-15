# [M] Manyfold vulnerable to session hijack via cookie leakage in proxy caches

## Summary
Severity: Medium
Advisory: CVE-2026-27933
Aliases: GHSA-g949-hmvj-2r76
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27933
Type: osv

## Details
Manyfold is an open source, self-hosted web application for managing a collection of 3d models, particularly focused on 3d printing. Versions prior to 0.133.0 are vulnerable to session hijack via cookie leakage in proxy caches. Version 0.133.0 fixes the issue.

## References
- https://github.com/manyfold3d/manyfold/releases/tag/v0.133.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27933.json
- https://github.com/manyfold3d/manyfold/security/advisories/GHSA-g949-hmvj-2r76
- https://nvd.nist.gov/vuln/detail/CVE-2026-27933
