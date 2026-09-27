# [H] CVE-2026-61371

## Summary
Severity: High
Advisory: CVE-2026-61371
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61371
Type: osv

## Details
Microsoft AVML before 0.17.0 could follow a symlink when opening a destination output path on Unix, allowing truncation/overwrite of the symlink target. The destructive effect is performed at open-time via O_TRUNC, and can happen before full input validation completes (“truncation-before-validation”).

## References
- https://gist.github.com/thesmartshadow/2d099071f847de8db3dc4bbaf4dfa6df
- https://github.com/microsoft/avml/releases/tag/v0.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61371
- https://github.com/microsoft/avml/pull/754
