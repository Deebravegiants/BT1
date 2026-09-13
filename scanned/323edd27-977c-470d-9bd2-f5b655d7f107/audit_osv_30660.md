# [H] liboqs has a correctness error in HQC decapsulation

## Summary
Severity: High
Advisory: CVE-2024-54137
Aliases: GHSA-gpf4-vrrw-r8v7
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-12-06
Source: https://osv.dev/vulnerability/CVE-2024-54137
Type: osv

## Details
liboqs is a C-language cryptographic library that provides implementations of post-quantum cryptography algorithms. A correctness error has been identified in the reference implementation of the HQC key encapsulation mechanism. Due to an indexing error, part of the secret key is incorrectly treated as non-secret data. This results in an incorrect shared secret value being returned when the decapsulation function is called with a malformed ciphertext. This vulnerability is fixed in 0.12.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54137.json
- https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-gpf4-vrrw-r8v7
- https://nvd.nist.gov/vuln/detail/CVE-2024-54137
- https://github.com/open-quantum-safe/liboqs/commit/cce1bfde4e52c524b087b9687020d283fbde0f24
