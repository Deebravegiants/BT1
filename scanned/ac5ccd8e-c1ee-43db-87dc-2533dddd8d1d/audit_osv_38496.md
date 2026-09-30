# [C] Masa CMS unauthenticated SQL injection via altTable parameter in JSON API

## Summary
Severity: Critical
Advisory: CVE-2026-40331
Aliases: GHSA-jphh-r686-6w7j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-40331
Type: osv

## Details
Masa CMS is an open source content management system. In versions 7.2.0 through 7.2.9, 7.3.0 through 7.3.14, 7.4.0 through 7.4.9, and 7.5.0 through 7.5.2, the unauthenticated JSON API accepts an altTable parameter that is stored via the setAltTable() method without validation or sanitization. This value is injected directly into a SQL FROM clause within feedGateway.cfc. An unauthenticated attacker can pass an arbitrary subquery into the altTable parameter to read sensitive data from any table in the database in a single HTTP request, including administrative credentials and password reset tokens.

This issue has been fixed in versions 7.2.10, 7.3.15, 7.4.10, and 7.5.3. As a workaround, apply validation to the setAltTable function in core/mura/content/feed/feedBean.cfc to restrict input to simple alphanumeric table names, or disable the JSON API if it is not required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40331.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-jphh-r686-6w7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40331
