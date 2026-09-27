# [H] Roxy-WI has a Command Injection via diff parameter in config comparison allows authenticated RCE

## Summary
Severity: High
Advisory: CVE-2026-27811
Aliases: GHSA-jvmv-cw47-jh77
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-27811
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Prior to version 8.2.6.3, a command injection vulnerability exists in the `/config/compare/<service>/<server_ip>/show` endpoint, allowed authenticated users to execute arbitrary system commands on the app host. The vulnerability exists in `app/modules/config/config.py` on line 362, where user input is directly formatted in the template string that is eventually executed. Version 8.2.6.3 fixes the issue.

## References
- https://github.com/roxy-wi/roxy-wi/releases/tag/v8.2.6.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27811.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-jvmv-cw47-jh77
- https://nvd.nist.gov/vuln/detail/CVE-2026-27811
- https://github.com/roxy-wi/roxy-wi/commit/a10ac7306c252014f97a7213db4a9470300fa064
