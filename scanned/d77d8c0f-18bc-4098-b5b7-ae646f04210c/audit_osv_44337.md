# [M] wolfEngine reuses the AES-CCM nonce on TLS 1.2 / DTLS 1.2 records

## Summary
Severity: Medium
Advisory: CVE-2026-81341
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-81341
Type: osv

## Details
wolfEngine before 1.4.1 sources the explicit AES-CCM nonce for TLS 1.2 and DTLS 1.2 records from the record input buffer instead of the TLS sequence number carried in the additional authenticated data. Because the record layer leaves the explicit-nonce field for the cipher to populate, the value read is constant across records, so every AES-CCM record within a connection is encrypted under an identical key and nonce pair. Reusing a CCM key and nonce weakens confidentiality (identical keystream across records, so a known record recovers the others) and integrity (authentication tag forgery). Only wolfEngine is affected; wolfProvider is not. AES-GCM under wolfEngine is tracked separately. AES-CCM cipher suites are not enabled by default and must be explicitly selected, which limits exposure. TLS 1.3 and non-TLS use of the cipher are not affected.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81341.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81341
- https://github.com/wolfSSL/wolfengine
