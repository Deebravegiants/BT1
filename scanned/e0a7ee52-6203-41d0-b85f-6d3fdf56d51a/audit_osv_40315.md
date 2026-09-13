# [M] Stack Buffer Overflow in wolfSSL PKCS7 wc_PKCS7_DecryptOri() via Oversized OID

## Summary
Severity: Medium
Advisory: CVE-2026-5295
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5295
Type: osv

## Details
A stack buffer overflow exists in wolfSSL's PKCS7 implementation in the wc_PKCS7_DecryptOri() function in wolfcrypt/src/pkcs7.c. When processing a CMS EnvelopedData message containing an OtherRecipientInfo (ORI) recipient, the function copies an ASN.1-parsed OID into a fixed 32-byte stack buffer (oriOID[MAX_OID_SZ]) via XMEMCPY without first validating that the parsed OID length does not exceed MAX_OID_SZ. A crafted CMS EnvelopedData message with an ORI recipient containing an OID longer than 32 bytes triggers a stack buffer overflow. Exploitation requires the library to be built with --enable-pkcs7 (disabled by default) and the application to have registered an ORI decrypt callback via wc_PKCS7_SetOriDecryptCb().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5295.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5295
- https://github.com/wolfSSL/wolfssl/pull/10116
- https://github.com/wolfSSL/wolfssl
