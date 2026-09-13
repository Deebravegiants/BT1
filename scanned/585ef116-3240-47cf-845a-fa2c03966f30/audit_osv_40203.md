# [M] CVE-2026-50811

## Summary
Severity: Medium
Advisory: CVE-2026-50811
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-50811
Type: osv

## Details
An out-of-bounds read vulnerability exists in FreeType 2.14.3 and versions before commit 5a280ecde6f324de0d226261036e736e0cb49a71 in src/truetype/ttgxvar.c, in the TT_Get_Var_Design implementation used by FT_Get_Var_Design_Coordinates

## References
- https://gist.github.com/junius-sec/6dd0fb25b643f89914083a38e5e57ace
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50811.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50811
- https://gitlab.freedesktop.org/freetype/freetype/-/issues/1436
- https://github.com/freetype/freetype/commit/5a280ecde6f324de0d226261036e736e0cb49a71
- https://gitlab.freedesktop.org/freetype/freetype/-/commit/5a280ecde6f324de0d226261036e736e0cb49a71
- https://gitlab.freedesktop.org/freetype/freetype/-/work_items/1436
