# [H] Server-Side Request Forgery in Jodd HTTP

## Summary
Severity: High
Advisory: GHSA-pp3c-cf6j-m3ff
CVE: CVE-2022-29631
CWE: CWE-74, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-07
Source: https://github.com/advisories/GHSA-pp3c-cf6j-m3ff
Type: github-advisory

## Affected
- Maven: `org.jodd:jodd-http` — affected >=5.0.0 <6.2.1

## Details
Jodd HTTP v6.0.9 was discovered to contain multiple CLRF injection vulnerabilities via the components jodd.http.HttpRequest#set and `jodd.http.HttpRequest#send. These vulnerabilities allow attackers to execute Server-Side Request Forgery (SSRF) via a crafted TCP payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29631
- https://github.com/oblac/jodd-http/issues/9
- https://github.com/oblac/jodd/issues/787
- https://github.com/oblac/jodd-http/commit/e50f573c8f6a39212ade68c6eb1256b2889fa8a6
- https://github.com/oblac/jodd-http
