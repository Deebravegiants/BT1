# [M] TinyWeb: HTTP Header Control Character Injection into CGI Environment

## Summary
Severity: Medium
Advisory: CVE-2026-29046
Aliases: GHSA-r3gf-pg2c-m7mc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:L)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29046
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. Prior to version 2.04, TinyWeb accepts request header values and later maps them into CGI environment variables (HTTP_*). The parser did not strictly reject dangerous control characters in header lines and header values, including CR, LF, and NUL, and did not consistently defend against encoded forms such as %0d, %0a, and %00. This can enable header value confusion across parser boundaries and may create unsafe data in the CGI execution context. This issue has been patched in version 2.04.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29046.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-r3gf-pg2c-m7mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-29046
- https://github.com/maximmasiutin/TinyWeb/commit/53aa8b6e5146491d7be57920e3fc50d7a34e4d5a
