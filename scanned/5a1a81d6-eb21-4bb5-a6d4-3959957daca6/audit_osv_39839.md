# [M] Deterministic AES/CBC Encryption in Spring Security AesBytesEncryptor Allows Ciphertext Correlation

## Summary
Severity: Medium
Advisory: CVE-2026-47842
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47842
Type: osv

## Details
Applications using AesBytesEncryptor with the two-argument constructor or when passing a null IV generator and CBC as the encryption mode encrypt data with AES/CBC using a null (all-zero) initialization vector.
Spring Security 7.1.0
Spring Security 7.0.0 - 7.0.6
Spring Security 6.5.0 - 6.5.11
Spring Security 6.4.0 - 6.4.18
Spring Security 5.8.0 - 5.8.27
Spring Security 5.7.0 - 5.7.25

## References
- https://spring.io/security/cve-2026-47842
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47842.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47842
