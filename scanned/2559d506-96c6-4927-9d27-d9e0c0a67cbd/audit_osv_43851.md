# [M] PKCS7_verify signer confusion allows forged signatures to be accepted

## Summary
Severity: Medium
Advisory: CVE-2026-7511
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-7511
Type: osv

## Details
PKCS7_verify signer confusion allows forged signatures, where the signer associated with a signature is not correctly bound, permitting a forged signature to be accepted.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7511.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7511
- https://github.com/wolfSSL/wolfssl/pull/10203
- https://github.com/wolfSSL/wolfssl
