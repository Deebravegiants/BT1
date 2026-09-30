# [H] http-cache-semantics vulnerable to Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-rc47-6667-2j5j
CVE: CVE-2022-25881
CWE: CWE-1333
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-rc47-6667-2j5j
Type: github-advisory

## Affected
- npm: `http-cache-semantics` — affected >=0 <4.1.1
- Maven: `org.webjars.npm:http-cache-semantics` — affected >=0 <4.1.1

## Details
http-cache semantics contains an Inefficient Regular Expression Complexity , leading to Denial of Service. This affects versions of the package http-cache-semantics before 4.1.1. The issue can be exploited via malicious request header values sent to a server, when that server reads the cache policy from the request using this library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25881
- https://github.com/kornelski/http-cache-semantics/commit/560b2d8ef452bbba20ffed69dc155d63ac757b74
- https://github.com/kornelski/http-cache-semantics
- https://github.com/kornelski/http-cache-semantics/blob/master/index.js%23L83
- https://security.netapp.com/advisory/ntap-20230622-0008
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3253332
- https://security.snyk.io/vuln/SNYK-JS-HTTPCACHESEMANTICS-3248783
