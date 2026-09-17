# [M] OpenUSD File Parsing Use-After-Free Remote Code Execution Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-grjp-54v3-c442
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-grjp-54v3-c442
Type: github-advisory

## Affected
- PyPI: `usd-core` — affected >=0 <25.11

## Details
# Patch
This is fixed with [commit b953092](https://github.com/PixarAnimationStudios/OpenUSD/commit/b9530922b6a8ea72cd43661226b693fff8abbe4c), with the fix available in OpenUSD 25.11 and onwards.

# Summary
We have been advised by Zero Day Initiative that our usage of the USD framework may constitute a Use-After-Free Remote Code Execution Vulnerability. They have sent us the attached file illustrating the issue. Indeed, we see a use after free exception when running the file through our importer with an address sanitizer.

[zdi-23709-poc0.zip](https://github.com/user-attachments/files/17474297/zdi-23709-poc0.zip)

Thanks in advance.

## References
- https://github.com/PixarAnimationStudios/OpenUSD/security/advisories/GHSA-grjp-54v3-c442
- https://github.com/PixarAnimationStudios/OpenUSD/commit/b9530922b6a8ea72cd43661226b693fff8abbe4c
- https://github.com/PixarAnimationStudios/OpenUSD
