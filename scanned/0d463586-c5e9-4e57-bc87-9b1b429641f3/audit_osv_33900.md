# [M] liboqs secret-dependent branching in HQC reference implementation when compiled with Clang 17-20

## Summary
Severity: Medium
Advisory: CVE-2025-52473
Aliases: GHSA-qq3m-rq9v-jfgm
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-52473
Type: osv

## Details
liboqs is a C-language cryptographic library that provides implementations of post-quantum cryptography algorithms. Multiple secret-dependent branches have been identified in the reference implementation of the HQC key encapsulation mechanism when it is compiled with Clang for optimization levels above -O0 (-O1, -O2, etc). A proof-of-concept local attack exploits this secret-dependent information to recover the entire secret key. This vulnerability is fixed in 0.14.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52473.json
- https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-qq3m-rq9v-jfgm
- https://nvd.nist.gov/vuln/detail/CVE-2025-52473
- https://github.com/open-quantum-safe/liboqs/commit/4215362acbf69b88fe1777c4c052f154e29f9897
