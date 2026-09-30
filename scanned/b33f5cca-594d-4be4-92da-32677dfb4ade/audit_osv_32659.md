# [C] Pi-Hole AdminLTE Whitelist (now 'Web Allowlist') Remote Command Execution

## Summary
Severity: Critical
Advisory: CVE-2025-34087
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-34087
Type: osv

## Details
An authenticated command injection vulnerability exists in Pi-hole versions up to 3.3. When adding a domain to the allowlist via the web interface, the domain parameter is not properly sanitized, allowing an attacker to append OS commands to the domain string. These commands are executed on the underlying operating system with the privileges of the Pi-hole service user.




This behavior was present in the legacy AdminLTE interface and has since been patched in later versions.

## References
- https://pi-hole.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34087.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34087
- https://vulncheck.com/advisories/pihole-adminlte-whitelist-rce
- https://github.com/pi-hole/web/releases/tag/v4.0
- https://pulsesecurity.co.nz/advisories/pihole-v3.3-vulns
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/unix/http/pihole_whitelist_exec.rb
