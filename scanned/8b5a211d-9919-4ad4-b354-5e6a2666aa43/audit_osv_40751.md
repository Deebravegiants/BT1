# [H] cpp-httplib: TLS certificate chain verification bypassed for IP-literal hosts on Mbed TLS and wolfSSL backends

## Summary
Severity: High
Advisory: CVE-2026-54919
Aliases: GHSA-8ffh-4p95-g3p2
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-54919
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. In affected Mbed TLS backend versions from 0.31.0 through 0.46.1 and wolfSSL backend versions from 0.33.0 through 0.46.1, when cpp-httplib is built with CPPHTTPLIB_MBEDTLS_SUPPORT or CPPHTTPLIB_WOLFSSL_SUPPORT and a client connects to an IP-literal host with server certificate verification enabled, SSLClient and Client in HTTPS mode skip certificate chain validation and WebSocketClient on the Mbed TLS backend skips verification altogether, allowing a man-in-the-middle attacker positioned to intercept traffic to present a crafted certificate and read or modify the traffic. This issue is fixed in version 0.47.0.

## References
- https://github.com/yhirose/cpp-httplib/releases/tag/v0.47.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54919.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-8ffh-4p95-g3p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54919
- https://github.com/yhirose/cpp-httplib/commit/fa981cedae004ea9d946f1392b9dec22fac6fee6
