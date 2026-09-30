# [H] Command Injection on tinygltf

## Summary
Severity: High
Advisory: CVE-2022-3008
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-09-05
Source: https://osv.dev/vulnerability/CVE-2022-3008
Type: osv

## Details
The tinygltf library uses the C library function wordexp() to perform file path expansion on untrusted paths that are provided from the input file. This function allows for command injection by using backticks. An attacker could craft an untrusted path input that would result in a path expansion. We recommend upgrading to 2.6.0 or past commit 52ff00a38447f06a17eab1caa2cf0730a119c751

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=49053
- https://github.com/syoyo/tinygltf/blob/master/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3008.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3008
- https://www.debian.org/security/2022/dsa-5232
- https://github.com/syoyo/tinygltf/issues/368
- https://github.com/syoyo/tinygltf/commit/52ff00a38447f06a17eab1caa2cf0730a119c751
