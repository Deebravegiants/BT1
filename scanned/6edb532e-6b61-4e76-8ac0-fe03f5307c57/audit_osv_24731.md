# [H] Roxy-WI has Path Traversal vulnerability

## Summary
Severity: High
Advisory: CVE-2023-25802
Aliases: GHSA-qcmp-q5h3-784m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-13
Source: https://osv.dev/vulnerability/CVE-2023-25802
Type: osv

## Details
Roxy-WI is a Web interface for managing Haproxy, Nginx, Apache, and Keepalived servers. Versions prior to 6.3.6.0 don't correctly neutralize `dir/../filename` sequences, such as `/etc/nginx/../passwd`, allowing an actor to gain information about a server. Version 6.3.6.0 has a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25802.json
- https://github.com/hap-wi/roxy-wi/security/advisories/GHSA-qcmp-q5h3-784m
- https://nvd.nist.gov/vuln/detail/CVE-2023-25802
- https://github.com/hap-wi/roxy-wi/commit/0054f25da7cf8c7480452f48e39308b5e392dc67
