# [H] CVE-2019-11938

## Summary
Severity: High
Advisory: CVE-2019-11938
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2019-11938
Type: osv

## Details
Java Facebook Thrift servers would not error upon receiving messages declaring containers of sizes larger than the payload. As a result, malicious clients could send short messages which would result in a large memory allocation, potentially leading to denial of service. This issue affects Facebook Thrift prior to v2019.12.09.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-11938
- https://github.com/facebook/fbthrift/commit/08c2d412adb214c40bb03be7587057b25d053030
- https://github.com/facebook/fbthrift/commit/71c97ffdcb61cccf1f8267774e873e21ebd3ebd3
