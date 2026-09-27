# [M] Roxy-WI has an arbitrary file read vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-33077
Aliases: GHSA-c799-4ww6-q93w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-33077
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Prior to version 8.2.6.4, the oldconfig parameter in the haproxy_section_save interface has an arbitrary file read vulnerability. Version 8.2.6.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33077.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-c799-4ww6-q93w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33077
- https://github.com/roxy-wi/roxy-wi/commit/aecc7971959092fa93e93531f1ffcde33524b031
