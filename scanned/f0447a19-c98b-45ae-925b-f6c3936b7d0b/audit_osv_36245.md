# [H] Roxy-WI has a Command Injection via grep parameter in logs.py allows authenticated RCE

## Summary
Severity: High
Advisory: CVE-2026-22265
Aliases: GHSA-mmmf-vh7m-rm47
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2026-22265
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Prior to 8.2.8.2, command injection vulnerability exists in the log viewing functionality that allows authenticated users to execute arbitrary system commands. The vulnerability is in app/modules/roxywi/logs.py line 87, where the grep parameter is used twice - once sanitized and once raw. This vulnerability is fixed in 8.2.8.2.

## References
- https://github.com/roxy-wi/roxy-wi/releases/tag/v8.2.8.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22265.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-mmmf-vh7m-rm47
- https://nvd.nist.gov/vuln/detail/CVE-2026-22265
- https://github.com/roxy-wi/roxy-wi/commit/f040d3338c4ba6f66127487361592e32e0188eee
