# [C] sar2html OS Command Injection

## Summary
Severity: Critical
Advisory: CVE-2025-34030
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-20
Source: https://osv.dev/vulnerability/CVE-2025-34030
Type: osv

## Details
An OS command injection vulnerability exists in sar2html version 3.2.2 and prior via the plot parameter in index.php. The application fails to sanitize user-supplied input before using it in a system-level context. Remote, unauthenticated attackers can inject shell commands by appending them to the plot parameter (e.g., ?plot=;id) in a crafted GET request. The output of the command is displayed in the application's interface after interacting with the host selection UI. Successful exploitation leads to arbitrary command execution on the underlying system. Exploitation evidence was observed by the Shadowserver Foundation on 2025-02-04 UTC.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34030.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34030
- https://vulncheck.com/advisories/sar2html-command-injection
- https://www.fortiguard.com/encyclopedia/ips/48624
- https://github.com/cemtan/sar2html
- https://www.exploit-db.com/exploits/47204
