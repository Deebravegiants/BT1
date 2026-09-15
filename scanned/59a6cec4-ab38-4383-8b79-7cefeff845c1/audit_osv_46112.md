# [H] A stack buffer overflow vulnerability exists in wolfSSL's PKCS7 SignedData encoding functionality

## Summary
Severity: High
Advisory: JLSEC-2026-691
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-691
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
A stack buffer overflow vulnerability exists in wolfSSL's PKCS7 SignedData encoding functionality. In `wc_PKCS7_BuildSignedAttributes()`, when adding custom signed attributes, the code passes an incorrect capacity value (esd->signedAttribsCount) to EncodeAttributes() instead of the remaining available space in the fixed-size signedAttribs[7] array. When an application sets pkcs7->signedAttribsSz to a value greater than `MAX_SIGNED_ATTRIBS_SZ` (default 7) minus the number of default attributes already added, EncodeAttributes() writes beyond the array bounds, causing stack memory corruption. In `WOLFSSL_SMALL_STACK` builds, this becomes heap corruption. Exploitation requires an application that allows untrusted input to control the signedAttribs array size when calling `wc_PKCS7_EncodeSignedData()` or related signing functions.

## References
- https://github.com/advisories/GHSA-3cr6-hpf3-2hmg
- https://github.com/wolfSSL/wolfssl/pull/9630
- https://nvd.nist.gov/vuln/detail/CVE-2026-0819
