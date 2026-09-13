# [C] Easywall 0.3.1 - Authentication Bypass via Command Injection in /ports-save Endpoint

## Summary
Severity: Critical
Advisory: CVE-2024-58275
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2024-58275
Type: osv

## Details
Easywall 0.3.1 allows authenticated remote command execution via a command injection vulnerability in the /ports-save endpoint that suffers from a parameter injection flaw. Attackers can inject shell metacharacters to execute arbitrary commands on the server.

## References
- https://jpylypiw.github.io/easywall/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58275.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58275
- https://www.vulncheck.com/advisories/easywall-031-authentication-bypass-via-command-injection-in-ports-save-endpoint
- https://github.com/jpylypiw/easywall
- https://www.exploit-db.com/exploits/51856
