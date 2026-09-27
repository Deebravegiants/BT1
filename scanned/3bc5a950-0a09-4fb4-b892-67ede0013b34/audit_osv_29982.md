# [M] CVE-2024-48425

## Summary
Severity: Medium
Advisory: CVE-2024-48425
Aliases: PYSEC-2024-293
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-48425
Type: osv

## Details
A segmentation fault (SEGV) was detected in the Assimp::SplitLargeMeshesProcess_Triangle::UpdateNode function within the Assimp library during fuzz testing using AddressSanitizer. The crash occurs due to a read access violation at address 0x000000000460, which points to the zero page, indicating a null or invalid pointer dereference.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48425.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48425
- https://github.com/assimp/assimp/issues/5791
