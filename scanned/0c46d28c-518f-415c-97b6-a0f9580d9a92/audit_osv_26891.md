# [C] Webgrind 1.1 - Remote Command Execution (RCE) via dataFile Parameter

## Summary
Severity: Critical
Advisory: CVE-2023-54339
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2023-54339
Type: osv

## Details
Webgrind 1.1 contains a remote command execution vulnerability that allows unauthenticated attackers to inject OS commands via the dataFile parameter in index.php. Attackers can execute arbitrary system commands by manipulating the dataFile parameter, such as using payload '0%27%26calc.exe%26%27' to execute commands on the target system.

## References
- http://github.com/jokkedk/webgrind/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54339.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54339
- https://www.vulncheck.com/advisories/webgrind-remote-command-execution-rce-via-datafile-parameter
- https://www.exploit-db.com/exploits/51074
