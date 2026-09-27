# [H] CVE-2019-3565

## Summary
Severity: High
Advisory: CVE-2019-3565
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-06
Source: https://osv.dev/vulnerability/CVE-2019-3565
Type: osv

## Details
Legacy C++ Facebook Thrift servers (using cpp instead of cpp2) would not error upon receiving messages with containers of fields of unknown type. As a result, malicious clients could send short messages which would take a long time for the server to parse, potentially leading to denial of service. This issue affects Facebook Thrift prior to v2019.05.06.00.

## References
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26%40%3Ccommits.pulsar.apache.org%3E
- http://www.securityfocus.com/bid/108280
- https://www.facebook.com/security/advisories/cve-2019-3565
- https://github.com/facebook/fbthrift/commit/01686e15ec77ccb4d49a77d5bce3a01601e54d64
