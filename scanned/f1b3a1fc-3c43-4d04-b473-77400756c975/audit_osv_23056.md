# [M] CVE-2022-42961

## Summary
Severity: Medium
Advisory: CVE-2022-42961
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-15
Source: https://osv.dev/vulnerability/CVE-2022-42961
Type: osv

## Details
An issue was discovered in wolfSSL before 5.5.0. A fault injection attack on RAM via Rowhammer leads to ECDSA key disclosure. Users performing signing operations with private ECC keys, such as in server-side TLS connections, might leak faulty ECC signatures. These signatures can be processed via an advanced technique for ECDSA key recovery. (In 5.5.0 and later, WOLFSSL_CHECK_SIG_FAULTS can be used to address the vulnerability.)

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.5.0-stable
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42961.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42961
