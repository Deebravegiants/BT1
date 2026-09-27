# [H] CVE-2019-3553

## Summary
Severity: High
Advisory: CVE-2019-3553
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2019-3553
Type: osv

## Details
C++ Facebook Thrift servers would not error upon receiving messages declaring containers of sizes larger than the payload. As a result, malicious clients could send short messages which would result in a large memory allocation, potentially leading to denial of service. This issue affects Facebook Thrift prior to v2020.02.03.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-3553
- https://github.com/facebook/fbthrift/commit/3f156207e8a6583d88999487e954320dc18955e6
- https://github.com/facebook/fbthrift/commit/c9a903e5902834e95bbd4ab0e9fa53ba0189f351
