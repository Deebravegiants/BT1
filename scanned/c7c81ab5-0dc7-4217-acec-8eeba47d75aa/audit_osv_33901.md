# [M] HTTP.jl vulnerable to CR/LF Injection in URIs

## Summary
Severity: Medium
Advisory: CVE-2025-52479
Aliases: GHSA-4g68-4pxg-mw93, JLSEC-2025-1
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-52479
Type: osv

## Details
HTTP.jl provides HTTP client and server functionality for Julia, and URIs.jl parses and works with Uniform Resource Identifiers (URIs). URIs.jl prior to version 1.6.0 and HTTP.jl prior to version 1.10.17 allows the construction of URIs containing CR/LF characters. If user input was not otherwise escaped or protected, this can lead to a CRLF injection attack. Users of HTTP.jl should upgrade immediately to HTTP.jl v1.10.17, and users of URIs.jl should upgrade immediately to URIs.jl v1.6.0. The check for valid URIs is now in the URI.jl package, and the latest version of HTTP.jl incorporates that fix. As a workaround, manually validate any URIs before passing them on to functions in this package.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52479.json
- https://github.com/JuliaWeb/HTTP.jl/security/advisories/GHSA-4g68-4pxg-mw93
- https://nvd.nist.gov/vuln/detail/CVE-2025-52479
- https://github.com/JuliaWeb/HTTP.jl/commit/e124953f388e7750f893fcf90efc72b7a59e35eb
- https://github.com/JuliaWeb/URIs.jl/pull/66
