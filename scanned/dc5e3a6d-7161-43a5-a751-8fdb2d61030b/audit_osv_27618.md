# [H] CVE-2024-24267

## Summary
Severity: High
Advisory: CVE-2024-24267
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24267
Type: osv

## Details
gpac v2.2.1 (fixed in v2.4.0) was discovered to contain a memory leak via the gfio_blob variable in the gf_fileio_from_blob function.

## References
- https://github.com/yinluming13579/gpac_defects/blob/main/gpac_3.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24267.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24267
- https://github.com/gpac/gpac/issues/2571
- https://github.com/NixOS/nixpkgs/pull/305402
- https://github.com/gpac/gpac/commit/d28d9ba45cf4f628a7b2c351849a895e6fcf2234
