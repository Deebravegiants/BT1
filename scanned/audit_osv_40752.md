# [M] Improper Validation of AES-GCM Authentication Tag Length in PKCS#7 Envelope Allows Authentication Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-5500
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5500
Type: osv

## Details
wolfSSL's wc_PKCS7_DecodeAuthEnvelopedData() does not properly sanitize the AES-GCM authentication tag length received and has no lower bounds check. A man-in-the-middle can therefore truncate the mac field from 16 bytes to 1 byte, reducing the tag check from 2⁻¹²⁸ to 2⁻⁸.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5500.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5500
- https://github.com/wolfSSL/wolfssl/pull/10102
