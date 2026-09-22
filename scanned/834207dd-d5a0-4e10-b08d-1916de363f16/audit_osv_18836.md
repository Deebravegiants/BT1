# [H] CVE-2020-36406

## Summary
Severity: High
Advisory: CVE-2020-36406
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2020-36406
Type: osv

## Details
uWebSockets 18.11.0 and 18.12.0 has a stack-based buffer overflow in uWS::TopicTree::trimTree (called from uWS::TopicTree::unsubscribeAll). NOTE: the vendor's position is that this is "a minor issue or not even an issue at all" because the developer of an application (that uses uWebSockets) should not be allowing the large number of triggered topics to accumulate

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/uwebsockets/OSV-2020-1695.yaml
- https://github.com/uNetworking/uWebSockets/commit/03fca626a95130ab80f86adada54b29d27242759
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25381
