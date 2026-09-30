# [M] cpp-httplib: Stack Overflow Denial of Service (DoS) via std::regex in multipart filename parsing

## Summary
Severity: Medium
Advisory: CVE-2026-29076
Aliases: GHSA-qq6v-r583-3h69
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-29076
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to version 0.37.0, cpp-httplib uses std::regex (libstdc++) to parse RFC 5987 encoded filename* values in multipart Content-Disposition headers. The regex engine in libstdc++ implements backtracking via deep recursion, consuming one stack frame per input character. An attacker can send a single HTTP POST request with a crafted filename* parameter that causes uncontrolled stack growth, resulting in a stack overflow (SIGSEGV) that crashes the server process. This issue has been patched in version 0.37.0.

## References
- https://github.com/yhirose/cpp-httplib/releases/tag/v0.37.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29076.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-qq6v-r583-3h69
- https://nvd.nist.gov/vuln/detail/CVE-2026-29076
- https://github.com/yhirose/cpp-httplib/commit/de296af3eb5b0d5c116470e033db900e4812c5e6
