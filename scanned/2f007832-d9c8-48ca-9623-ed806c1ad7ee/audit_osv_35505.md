# [H] Stack buffer overflow in PKCS7 SignedData encoding with custom signed attributes

## Summary
Severity: High
Advisory: CVE-2026-0819
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-0819
Type: osv

## Details
A stack buffer overflow vulnerability exists in wolfSSL's PKCS7 SignedData encoding functionality. In wc_PKCS7_BuildSignedAttributes(), when adding custom signed attributes, the code passes an incorrect capacity value (esd->signedAttribsCount) to EncodeAttributes() instead of the remaining available space in the fixed-size signedAttribs[7] array. When an application sets pkcs7->signedAttribsSz to a value greater than MAX_SIGNED_ATTRIBS_SZ (default 7) minus the number of default attributes already added, EncodeAttributes() writes beyond the array bounds, causing stack memory corruption. In WOLFSSL_SMALL_STACK builds, this becomes heap corruption. Exploitation requires an application that allows untrusted input to control the signedAttribs array size when calling wc_PKCS7_EncodeSignedData() or related signing functions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0819.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0819
- https://github.com/wolfSSL/wolfssl/pull/9630
- https://github.com/wolfSSL/wolfssl
