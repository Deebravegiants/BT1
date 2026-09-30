# [M] CVE-2026-34085

## Summary
Severity: Medium
Advisory: CVE-2026-34085
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-34085
Type: osv

## Details
fontconfig before 2.17.1 has an off-by-one error in allocation during sfnt capability handling, leading to a one-byte out-of-bounds write, and potentially a crash or code execution. This is in FcFontCapabilities in fcfreetype.c.

## References
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/work_items/481
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34085.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34085
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/commit/b9bec06d73340f1b5727302d13ac3df307b7febc
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/merge_requests/446
