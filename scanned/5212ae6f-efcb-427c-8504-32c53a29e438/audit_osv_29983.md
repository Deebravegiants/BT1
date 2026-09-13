# [M] CVE-2024-48426

## Summary
Severity: Medium
Advisory: CVE-2024-48426
Aliases: PYSEC-2024-294
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-48426
Type: osv

## Details
A segmentation fault (SEGV) was detected in the SortByPTypeProcess::Execute function in the Assimp library during fuzz testing with AddressSanitizer. The crash occurred due to a read access to an invalid memory address (0x1000c9714971).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48426.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48426
- https://github.com/assimp/assimp/issues/5789
