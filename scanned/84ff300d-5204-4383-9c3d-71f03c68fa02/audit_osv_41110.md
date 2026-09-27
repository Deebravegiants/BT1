# [M] CVE-2026-57826

## Summary
Severity: Medium
Advisory: CVE-2026-57826
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-57826
Type: osv

## Details
An issue was discovered in openHiTLS 0.2.0 through 0.3.2. In the X.509 certificate chain verification, the basic constraints extension and CA flag processing of intermediate CAs are only verified for v3 certificates, and v1/v2 certificates are ignored.

## References
- https://gitcode.com/openHiTLS/openhitls/pull/1399
- https://gitcode.com/openHiTLS/openhitls/pull/1657
- https://github.com/openHiTLS/openHiTLS/compare/openhitls-0.3.2...openhitls-0.3.3
- https://www.openhitls.net/zh/support/HTLS-2026-001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57826.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57826
- https://github.com/openHiTLS/openHiTLS/commit/2d3b221d113b452bc197012b185978b8314ee8a4
- https://github.com/openHiTLS/openHiTLS/commit/4355cdf5b043d5b9ef698f8f57860f77f8e92561
