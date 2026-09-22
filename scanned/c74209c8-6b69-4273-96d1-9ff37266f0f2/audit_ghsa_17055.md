# [M] Go JOSE vulnerable to Improper Handling of Highly Compressed Data (Data Amplification)

## Summary
Severity: Medium
Advisory: GHSA-c5q2-7r4c-mv6g
CVE: CVE-2024-28180
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-c5q2-7r4c-mv6g
Type: github-advisory

## Affected
- Go: `github.com/go-jose/go-jose/v4` — affected >=0 <4.0.1
- Go: `github.com/go-jose/go-jose/v3` — affected >=0 <3.0.3
- Go: `gopkg.in/go-jose/go-jose.v2` — affected >=0 <2.6.3
- Go: `gopkg.in/square/go-jose.v2` — affected >=0

## Details
### Impact
An attacker could send a JWE containing compressed data that used large amounts of memory and CPU when decompressed by Decrypt or DecryptMulti. Those functions now return an error if the decompressed data would exceed 250kB or 10x the compressed size (whichever is larger). Thanks to Enze Wang@Alioth and Jianjun Chen@Zhongguancun Lab (@zer0yu and @chenjj) for reporting.

### Patches
The problem is fixed in the following packages and versions:
- github.com/go-jose/go-jose/v4 version 4.0.1
- github.com/go-jose/go-jose/v3 version 3.0.3
- gopkg.in/go-jose/go-jose.v2 version 2.6.3

The problem will not be fixed in the following package because the package is archived:
- gopkg.in/square/go-jose.v2

## References
- https://github.com/go-jose/go-jose/security/advisories/GHSA-c5q2-7r4c-mv6g
- https://nvd.nist.gov/vuln/detail/CVE-2024-28180
- https://github.com/go-jose/go-jose/commit/0dd4dd541c665fb292d664f77604ba694726f298
- https://github.com/go-jose/go-jose/commit/add6a284ea0f844fd6628cba637be5451fe4b28a
- https://github.com/go-jose/go-jose/commit/f4c051a0653d78199a053892f7619ebf96339502
- https://github.com/go-jose/go-jose
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GD2GSBQTBLYADASUBHHZV2CZPTSLIPQJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I6MMWFBOXJA6ZCXNVPDFJ4XMK5PVG5RG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IJ6LAJJ2FTA2JVVOACCV5RZTOIZLXUNJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JNPMXL36YGS3GQEVI3Q5HKHJ7YAAQXL5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KXKGNCRU7OTM5AHC7YIYBNOWI742PRMY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MSOMHDKRPU3A2JEMRODT2IREDFBLVPGS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UG5FSEYJ3GP27FZXC5YAAMMEC5XWKJHG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UJO2U5ACZVACNQXJ5EBRFLFW6DP5BROY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XJDO5VSIAOGT2WP63AXAAWNRSVJCNCRH
