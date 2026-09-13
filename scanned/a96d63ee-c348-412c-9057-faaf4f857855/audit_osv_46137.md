# [M] JLSEC-2026-719

## Summary
Severity: Medium
Advisory: JLSEC-2026-719
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-719
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A stack buffer overflow exists in wolfSSL's PKCS7 implementation in the `wc_PKCS7_DecryptOri()` function in `wolfcrypt/src/pkcs7.c`. When processing a CMS EnvelopedData message containing an OtherRecipientInfo (ORI) recipient, the function copies an ASN.1-parsed OID into a fixed 32-byte stack buffer (oriOID[`MAX_OID_SZ`]) via XMEMCPY without first validating that the parsed OID length does not exceed `MAX_OID_SZ`. A crafted CMS EnvelopedData message with an ORI recipient containing an OID longer than 32 bytes triggers a stack buffer overflow. Exploitation requires the library to be built with --enable-pkcs7 (disabled by default) and the application to have registered an ORI decrypt callback via `wc_PKCS7_SetOriDecryptCb()`.

## References
- https://github.com/wolfSSL/wolfssl/pull/10116
