# [M] aiohttp's HTTP parser (the python one, not llhttp) still overly lenient about separators

## Summary
Severity: Medium
Advisory: GHSA-8qpw-xqxj-h4r2
CVE: CVE-2024-23829
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-01-29
Source: https://github.com/advisories/GHSA-8qpw-xqxj-h4r2
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.9.2

## Details
### Summary
Security-sensitive parts of the *Python HTTP parser* retained minor differences in allowable character sets, that must trigger error handling to robustly match frame boundaries of proxies in order to protect against injection of additional requests. Additionally, validation could trigger exceptions that were not handled consistently with processing of other malformed input.

### Details
These problems are rooted in pattern matching protocol elements, previously improved by PR #3235 and GHSA-gfw2-4jvh-wgfg:

1. The expression `HTTP/(\d).(\d)` lacked another backslash to clarify that the separator should be a literal dot, not just *any* Unicode code point (result: `HTTP/(\d)\.(\d)`).

2. The HTTP version was permitting Unicode digits, where only ASCII digits are standards-compliant.

3. Distinct regular expressions for validating HTTP Method and Header field names were used - though both should (at least) apply the common restrictions of rfc9110 `token`.

### PoC
`GET / HTTP/1ö1`
`GET / HTTP/1.𝟙`
`GET/: HTTP/1.1`
`Content-Encoding?: chunked`

### Impact
Primarily concerns running an aiohttp server without llhttp:
 1. **behind a proxy**: Being more lenient than internet standards require could, depending on deployment environment, assist in request smuggling.
 2. **directly accessible** or exposed behind proxies relaying malformed input: the unhandled exception could cause excessive resource consumption on the application server and/or its logging facilities.

-----

Patch: https://github.com/aio-libs/aiohttp/pull/8074/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-8qpw-xqxj-h4r2
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-gfw2-4jvh-wgfg
- https://nvd.nist.gov/vuln/detail/CVE-2024-23829
- https://github.com/aio-libs/aiohttp/pull/3235
- https://github.com/aio-libs/aiohttp/pull/8074
- https://github.com/aio-libs/aiohttp/pull/8074/files
- https://github.com/aio-libs/aiohttp/commit/33ccdfb0a12690af5bb49bda2319ec0907fa7827
- https://github.com/aio-libs/aiohttp
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2024-26.yaml
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ICUOCFGTB25WUT336BZ4UNYLSZOUVKBD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XXWVZIVAYWEBHNRIILZVB3R3SDQNNAA7
