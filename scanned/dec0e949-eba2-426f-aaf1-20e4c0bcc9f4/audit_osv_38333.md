# [H] CVE-2026-38976

## Summary
Severity: High
Advisory: CVE-2026-38976
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-38976
Type: osv

## Details
mrubyc through 3.4.1 was found to contain a NULL pointer dereference in src/vm.c in op_super() / OP_SUPER due to a missing runtime guard for top-level super.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38976.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38976
- https://github.com/mrubyc/mrubyc/issues/276
- https://github.com/hayat01sh1da/mrubyc/commit/c4aa2a06bfdd13a0f1ae5165c5760a2530314a42
- https://github.com/mrubyc/mrubyc
