# [M] CVE-2023-6992

## Summary
Severity: Medium
Advisory: CVE-2023-6992
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-04
Source: https://osv.dev/vulnerability/CVE-2023-6992
Type: osv

## Details
Cloudflare version of zlib library was found to be vulnerable to memory corruption issues affecting the deflation algorithm implementation (deflate.c). The issues resulted from improper input validation and heap-based buffer overflow.
A local attacker could exploit the problem during compression using a crafted malicious file potentially leading to denial of service of the software.
Patches: The issue has been patched in commit  8352d10 https://github.com/cloudflare/zlib/commit/8352d108c05db1bdc5ac3bdf834dad641694c13c . The upstream repository is not affected.

## References
- https://github.com/cloudflare/zlib/security/advisories/GHSA-vww9-j87r-4cqh
- https://github.com/cloudflare/zlib
