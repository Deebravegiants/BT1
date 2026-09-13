# [C] Roxy-WI Vulnerable to Authenticated Remote Code Execution via OS Command Injection in find-in-config Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-33208
Aliases: GHSA-7m2h-gmvj-cjx2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-33208
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. Prior to version 8.2.6.4, the /config/ < service > /find-in-config endpoint in Roxy-WI fails to sanitize the user-supplied words parameter before embedding it into a shell command string that is subsequently executed on a remote managed server via SSH. An authenticated attacker can inject arbitrary shell metacharacters to break out of the intended grep command context and execute arbitrary OS commands with sudo privileges on the target server, resulting in full Remote Code Execution (RCE). Version 8.2.6.4 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33208.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-7m2h-gmvj-cjx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33208
- https://github.com/roxy-wi/roxy-wi/commit/02f147d567a3cc8cf61a4b58ea4c2b7866a544de
