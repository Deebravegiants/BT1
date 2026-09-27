# [C] llhttp allows HTTP Request Smuggling via Improper Delimiting of Header Fields

## Summary
Severity: Critical
Advisory: GHSA-q5vx-44v4-gch4
CVE: CVE-2022-32214
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-q5vx-44v4-gch4
Type: github-advisory

## Affected
- npm: `llhttp` — affected >=0 <6.0.7

## Details
The llhttp parser in the http module in Node.js does not strictly use the CRLF sequence to delimit HTTP requests. The LF character (without CR) is sufficient to delimit HTTP header fields in the lihttp parser. According to RFC7230 section 3, only the CRLF sequence should delimit each header-field. This can lead to HTTP Request Smuggling (HRS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32214
- https://github.com/nodejs/llhttp/commit/18a4afc7ffb4e49dc9e2daebc50588199a6d1dbb
- https://hackerone.com/reports/1524692
- https://datatracker.ietf.org/doc/html/rfc7230#section-3
- https://nodejs.org/en/blog/vulnerability/july-2022-security-releases
- https://security.netapp.com/advisory/ntap-20220915-0001
- https://www.debian.org/security/2023/dsa-5326
