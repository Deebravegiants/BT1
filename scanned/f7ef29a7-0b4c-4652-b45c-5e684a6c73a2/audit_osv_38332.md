# [M] CVE-2026-38973

## Summary
Severity: Medium
Advisory: CVE-2026-38973
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-38973
Type: osv

## Details
mrubyc through release3.4.1 was found to contain an out-of-bounds read in builtin missing-method lookup inside mrbc_find_method().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38973.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38973
- https://github.com/mrubyc/mrubyc/issues/279%2C
- https://github.com/mrubyc/mrubyc/commit/f83a8b67ca1c7c62ac0dd548a363d79f767c4e30
- https://github.com/mrubyc/mrubyc
