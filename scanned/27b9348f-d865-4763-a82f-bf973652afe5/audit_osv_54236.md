# [M] CVE-2023-43898

## Summary
Severity: Medium
Advisory: CVE-2023-43898
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-43898
Type: osv

## Details
Nothings stb 2.28 was discovered to contain a Null Pointer Dereference via the function stbi__convert_format. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted pic file.

## References
- https://github.com/nothings/stb/issues/1452
- https://github.com/nothings/stb/pull/1454
- https://github.com/peccc/null-stb
