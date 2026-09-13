# [C] Unauthenticated Remote Code Execution in Roxy-wi

## Summary
Severity: Critical
Advisory: CVE-2022-31126
Aliases: GHSA-mh86-878h-43c9
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2022-31126
Type: osv

## Details
Roxy-wi is an open source web interface for managing Haproxy, Nginx, Apache and Keepalived servers. A vulnerability in Roxy-wi allows a remote, unauthenticated attacker to code execution by sending a specially crafted HTTP request to /app/options.py file. This affects Roxy-wi versions before 6.1.1.0. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31126.json
- https://github.com/hap-wi/roxy-wi/security/advisories/GHSA-mh86-878h-43c9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31126
