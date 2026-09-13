# [M] CVE-2025-61147

## Summary
Severity: Medium
Advisory: CVE-2025-61147
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-61147
Type: osv

## Details
strukturag libde265 commit d9fea9d wa discovered to contain a segmentation fault via the component decoder_context::compute_framedrop_table().

## References
- https://gist.github.com/optionGo/e6567a1c2bc4e0c9fee4e1e8be8d6af9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61147.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61147
- https://github.com/strukturag/libde265/issues/484
- https://github.com/strukturag/libde265/commit/8b17e0930f77db07f55e0b89399a8f054ddbecf7
