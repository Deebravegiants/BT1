# [M] Roxy-WI has Pre-Authentication LDAP Injection that Leads to Authentication Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-33432
Aliases: GHSA-hv3x-4w38-r92m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-33432
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions up to and including 8.2.8.2, when LDAP authentication is enabled, Roxy-WI constructs an LDAP search filter by directly concatenating the user-supplied login username into the filter string without escaping LDAP special characters. An unauthenticated attacker can inject LDAP filter metacharacters into the username field to manipulate the search query, cause the directory to return an unintended user entry, and bypass authentication entirely — gaining access to the application without knowing any valid password. As of time of publication, no known patches are available.

## References
- https://github.com/roxy-wi/roxy-wi/blob/v8.2.8.2/app/modules/roxywi/auth.py
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33432.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-hv3x-4w38-r92m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33432
