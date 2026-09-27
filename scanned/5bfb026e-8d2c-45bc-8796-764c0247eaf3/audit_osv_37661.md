# [H] cpp-httplib has a Silent TLS Certificate Verification Bypass on HTTPS Redirect via Proxy

## Summary
Severity: High
Advisory: CVE-2026-32627
Aliases: GHSA-c3h8-fqq4-xm4g
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32627
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.37.2, when a cpp-httplib client is configured with a proxy and set_follow_location(true), any HTTPS redirect it follows will have TLS certificate and hostname verification silently disabled on the new connection. The client will accept any certificate presented by the redirect target — expired, self-signed, or forged — without raising an error or notifying the application. A network attacker in a position to return a redirect response can fully intercept the follow-up HTTPS connection, including any credentials or session tokens in flight. This vulnerability is fixed in 0.37.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32627.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-c3h8-fqq4-xm4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32627
