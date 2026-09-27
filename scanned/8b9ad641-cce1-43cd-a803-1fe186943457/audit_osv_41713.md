# [H] Libevent: HTTP header handling bugs create risk of access control bypass.

## Summary
Severity: High
Advisory: CVE-2026-63385
Aliases: GHSA-jcwh-pvf2-73p2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63385
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent has two HTTP parsing weaknesses in http.c. evhttp_decode_uri_internal decodes percent-encoded %00 bytes into literal NUL characters, which can cause downstream C string operations to truncate a path and bypass validation performed on a different representation. evhttp_header_is_valid_value also accepts obsolete line folding in header values containing carriage return or line feed characters, allowing a proxy and libevent to interpret headers differently and enabling header injection or access control bypass. The CRLF header acceptance is fixed in versions 2.1.13 and 2.2.2-alpha, but the reviewed patches do not clearly remediate the URI NUL-truncation condition.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63385.json
- https://github.com/libevent/libevent/security/advisories/GHSA-jcwh-pvf2-73p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-63385
- https://github.com/libevent/libevent/commit/758be0c0f69c1934ef9a84ab39e9f9e5fde2e6d0
- https://github.com/libevent/libevent/commit/9170dd35e64714613e8d13b290587cfc28e258e2
