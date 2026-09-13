# [C] Pi-hole Web Interface has a Command Injection Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-33765
Aliases: GHSA-828h-5x96-rqx7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33765
Type: osv

## Details
Pi-hole Admin Interface is a web interface for managing Pi-hole, a network-level ad and internet tracker blocking application. Versions prior to 6.0 have a critical OS Command Injection vulnerability in the savesettings.php file. The application takes the user-controlled $_POST['webtheme'] parameter and concatenates it directly into a system command executed via PHP's exec() function. Since the input is neither sanitized nor validated before being passed to the shell, an attacker can append arbitrary system commands to the intended pihole command. Furthermore, because the command is executed with sudo privileges, the injected commands will run with elevated (likely root) privileges. Version 6.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33765.json
- https://github.com/pi-hole/web/security/advisories/GHSA-828h-5x96-rqx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33765
