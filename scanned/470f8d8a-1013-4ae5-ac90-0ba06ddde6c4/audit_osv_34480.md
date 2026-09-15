# [M] CVE-2025-60753

## Summary
Severity: Medium
Advisory: CVE-2025-60753
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-60753
Type: osv

## Details
An issue was discovered in libarchive bsdtar before version 3.8.1 in function apply_substitution in file tar/subst.c when processing crafted -s substitution rules. This can cause unbounded memory allocation and lead to denial of service (Out-of-Memory crash).

## References
- https://github.com/Papya-j/CVE/tree/main/CVE-2025-60753
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60753.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60753
- https://github.com/libarchive/libarchive/issues/2725
