# [M] cpp-httplib's default exception handler leaks e.what() to clients via EXCEPTION_WHAT response header

## Summary
Severity: Medium
Advisory: CVE-2026-28434
Aliases: GHSA-8mpw-r4gc-xm7q
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-28434
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.35.0, when a request handler throws a C++ exception and the application has not registered a custom exception handler via set_exception_handler(), the library catches the exception and writes its message directly into the HTTP response as a header named EXCEPTION_WHAT. This header is sent to whoever made the request, with no authentication check and no special configuration required to trigger it. The behavior is on by default. A developer who does not know to opt in to set_exception_handler() will ship a server that leaks internal exception messages to any client. This vulnerability is fixed in 0.35.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28434.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-8mpw-r4gc-xm7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28434
- https://github.com/yhirose/cpp-httplib/commit/defd907c7469c5c8281247b73bbd07be24c31164
