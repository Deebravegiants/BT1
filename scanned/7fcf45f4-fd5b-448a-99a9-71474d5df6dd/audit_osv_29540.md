# [H] OS Command Injection via Port Scan Functionality in Roxy-WI

## Summary
Severity: High
Advisory: CVE-2024-43804
Aliases: GHSA-qc52-vwwj-5585
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-43804
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. An OS Command Injection vulnerability allows any authenticated user on the application to execute arbitrary code on the web application server via port scanning functionality. User-supplied input is used without validation when constructing and executing an OS command. User supplied JSON POST data is parsed and if "id" JSON key does not exist, JSON value supplied via "ip" JSON key is assigned to the "ip" variable. Later on, "ip" variable which can be controlled by the attacker is used when constructing the cmd and cmd1 strings without any extra validation. Then, server_mod.subprocess_execute function is called on both cmd1 and cmd2. When the definition of the server_mod.subprocess_execute() function is analyzed, it can be seen that subprocess.Popen() is called on the input parameter with shell=True which results in OS Command Injection. This issue has not yet been patched. Users are advised to contact the Roxy-WI to coordinate a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43804.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-qc52-vwwj-5585
- https://nvd.nist.gov/vuln/detail/CVE-2024-43804
