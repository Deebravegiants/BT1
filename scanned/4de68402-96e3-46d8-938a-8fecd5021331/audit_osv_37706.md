# [M] Botan: Missing OCSP Response Signature Verification Allows MitM Certificate Revocation Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-32883
Aliases: GHSA-9j2j-hqmc-hf5x
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-32883
Type: osv

## Details
Botan is a C++ cryptography library. From version 3.0.0 to before version 3.11.0, during X509 path validation, OCSP responses were checked for an appropriate status code, but critically omitted verifying the signature of the OCSP response itself. This issue has been patched in version 3.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32883.json
- https://github.com/randombit/botan/security/advisories/GHSA-9j2j-hqmc-hf5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32883
