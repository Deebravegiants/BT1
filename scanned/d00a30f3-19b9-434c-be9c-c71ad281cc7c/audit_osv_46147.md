# [M] wolfSSL's `wc_PKCS7_DecodeAuthEnvelopedData()` does not properly sanitize the AES-GCM authentication...

## Summary
Severity: Medium
Advisory: JLSEC-2026-729
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-729
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
wolfSSL's `wc_PKCS7_DecodeAuthEnvelopedData()` does not properly sanitize the AES-GCM authentication tag length received and has no lower bounds check. A man-in-the-middle can therefore truncate the mac field from 16 bytes to 1 byte, reducing the tag check from 2⁻¹²⁸ to 2⁻⁸.

## References
- https://github.com/advisories/GHSA-m77r-vqw2-hffx
- https://github.com/wolfSSL/wolfssl/pull/10102
- https://nvd.nist.gov/vuln/detail/CVE-2026-5500
