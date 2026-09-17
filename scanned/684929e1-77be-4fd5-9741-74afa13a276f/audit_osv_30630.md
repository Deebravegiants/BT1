# [M] CVE-2024-53425

## Summary
Severity: Medium
Advisory: CVE-2024-53425
Aliases: PYSEC-2024-295
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53425
Type: osv

## Details
A heap-buffer-overflow vulnerability was discovered in the SkipSpacesAndLineEnd function in Assimp v5.4.3. This issue occurs when processing certain malformed MD5 model files, leading to an out-of-bounds read and potential application crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53425.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53425
- https://github.com/assimp/assimp/issues/5860
