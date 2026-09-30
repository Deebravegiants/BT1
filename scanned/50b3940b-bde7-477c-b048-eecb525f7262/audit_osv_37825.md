# [M] Roxy-WI Vulnerable to Authenticated Arbitrary File Read via Path Traversal in Config Version Viewer

## Summary
Severity: Medium
Advisory: CVE-2026-33431
Aliases: GHSA-w3c9-36jf-qrw4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-33431
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Prior to version 8.2.6.4, the POST /config/<service>/show API endpoint accepts a configver parameter that is directly appended to a base directory path to construct a local file path, which is subsequently opened and its contents returned to the caller. The existing path traversal guard only inspects the base directory variable (which is never user-controlled) and entirely ignores the user-supplied configver value. An authenticated attacker can supply a configver value containing `../` sequences to escape the intended directory and read arbitrary files accessible to the web application process. Version 8.2.6.4 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33431.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-w3c9-36jf-qrw4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33431
- https://github.com/roxy-wi/roxy-wi/commit/d4d100067dd0ee04317f05d3b51be8fcfdc3f802
