# [H] CVE-2026-34876

## Summary
Severity: High
Advisory: CVE-2026-34876
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34876
Type: osv

## Details
An issue was discovered in Mbed TLS 3.x before 3.6.6. An out-of-bounds read vulnerability in mbedtls_ccm_finish() in library/ccm.c allows attackers to obtain adjacent CCM context data via invocation of the multipart CCM API with an oversized tag_len parameter. This is caused by missing validation of the tag_len parameter against the size of the internal 16-byte authentication buffer. The issue affects the public multipart CCM API in Mbed TLS 3.x, where mbedtls_ccm_finish() can be invoked directly by applications. In Mbed TLS 4.x versions prior to the fix, the same missing validation exists in the internal implementation; however, the function is not exposed as part of the public API. Exploitation requires application-level invocation of the multipart CCM API.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34876.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-ccm-finish-boundary-check/
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2026-34876
