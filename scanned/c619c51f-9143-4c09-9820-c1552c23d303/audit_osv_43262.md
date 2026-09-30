# [H] unearth 0.18.2 Path Traversal via Unnormalized Paths and Symlink Escape

## Summary
Severity: High
Advisory: CVE-2026-73030
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-73030
Type: osv

## Details
unearth through 0.18.2, fixed in commit 6c78164, contains a path traversal vulnerability in the is_within_directory function that fails to normalize paths before validation, allowing ../ sequences to bypass directory containment checks. Attackers can supply malicious tar archives with symlink members or traversal sequences to write files to arbitrary filesystem locations accessible to the process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73030.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73030
- https://www.vulncheck.com/advisories/unearth-path-traversal-via-unnormalized-paths-and-symlink-escape
- https://github.com/frostming/unearth/pull/181
- https://github.com/frostming/unearth/commit/6c78164e7bfa28b8b3d6f247b87e560692e3c8ba
- https://github.com/frostming/unearth
- https://github.com/frostming/unearth/issues/180
