# [H] CVE-2025-13151

## Summary
Severity: High
Advisory: CVE-2025-13151
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-13151
Type: osv

## Details
Stack-based buffer overflow in libtasn1 version: v4.20.0. The function fails to validate the size of input data resulting in a buffer overflow in asn1_expend_octet_string.

## References
- http://www.openwall.com/lists/oss-security/2026/01/08/5
- https://www.kb.cert.org/vuls/id/271649
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13151.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13151
- https://gitlab.com/gnutls/libtasn1/-/merge_requests/121
- https://gitlab.com/gnutls/libtasn1
