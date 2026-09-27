# [C] LibreNMS before 26.5.0 Remote Code Execution via AboutController

## Summary
Severity: Critical
Advisory: CVE-2026-84190
Aliases: GHSA-jf24-8g2h-2wg7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84190
Type: osv

## Details
LibreNMS versions before 26.5.0 contain a remote code execution vulnerability in the AboutController where the snmpget configuration parameter is passed to shell_exec() without proper validation. An authenticated administrator can modify the snmpget configuration to point to a malicious executable file and trigger code execution by accessing the /about endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84190.json
- https://github.com/librenms/librenms/security/advisories/GHSA-jf24-8g2h-2wg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-84190
- https://www.vulncheck.com/advisories/librenms-before-26.5.0-remote-code-execution-via-aboutcontroller
