# [M] ASN.1 date parser overread

## Summary
Severity: Medium
Advisory: CVE-2024-7264
Aliases: CURL-CVE-2024-7264
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-7264
Type: osv

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
- https://hackerone.com/reports/2629968
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7264.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7264
- https://security.netapp.com/advisory/ntap-20240828-0008/
- https://security.netapp.com/advisory/ntap-20241025-0006/
- https://security.netapp.com/advisory/ntap-20241025-0010/
- https://github.com/curl/curl/commit/27959ecce75cdb2809c0bdb3286e60e08fadb519
