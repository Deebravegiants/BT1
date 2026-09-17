# [M] libcurl's ASN1 parser code has the `GTime2str()` function, used for parsing an ASN.1 Generalized...

## Summary
Severity: Medium
Advisory: JLSEC-2025-38
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-38
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.9.1+0
- Julia: `LibCURL_jll` — affected >=0 <8.9.1+0

## Details
libcurl's ASN1 parser code has the `GTime2str()` function, used for parsing an
ASN.1 Generalized Time field. If given an syntactically incorrect field, the
parser might end up using -1 for the length of the *time fraction*, leading to
a `strlen()` getting performed on a pointer to a heap buffer area that is not
(purposely) null terminated.

This flaw most likely leads to a crash, but can also lead to heap contents
getting returned to the application when
[CURLINFO_CERTINFO](https://curl.se/libcurl/c/CURLINFO_CERTINFO.html) is used.

## References
- http://www.openwall.com/lists/oss-security/2024/07/31/1
- https://curl.se/docs/CVE-2024-7264.html
- https://curl.se/docs/CVE-2024-7264.json
- https://github.com/curl/curl/commit/27959ecce75cdb2809c0bdb3286e60e08fadb519
- https://hackerone.com/reports/2629968
- https://security.netapp.com/advisory/ntap-20240828-0008/
- https://security.netapp.com/advisory/ntap-20241025-0006/
- https://security.netapp.com/advisory/ntap-20241025-0010/
