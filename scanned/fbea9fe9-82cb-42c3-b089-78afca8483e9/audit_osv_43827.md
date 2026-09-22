# [C] openssl_encrypt before 1.4.0 Authentication Bypass via AES-CTR Fallback

## Summary
Severity: Critical
Advisory: CVE-2026-74901
Aliases: GHSA-w4j7-wfgw-r52w, PYSEC-2026-3773
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74901
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain an authentication bypass vulnerability in pqc.py where AES-GCM decryption failures trigger fallback to unauthenticated AES-CTR mode. Attackers can modify ciphertext in transit to bypass integrity verification and perform bit-flipping attacks without detection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74901.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-w4j7-wfgw-r52w
- https://nvd.nist.gov/vuln/detail/CVE-2026-74901
- https://www.vulncheck.com/advisories/openssl-encrypt-before-authentication-bypass-via-aes-ctr-fallback
