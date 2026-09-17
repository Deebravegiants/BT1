# [C] wg-easy wg-easy - OS Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-72603
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72603
Type: osv

## Details
An OS command injection vulnerability in wg-easy 15.3.0 allows users with the clients.create permission to execute arbitrary commands as root by injecting newline-delimited WireGuard PostUp directives into the client name field. The client name is written to the WireGuard configuration file without neutralizing newline characters, allowing injection of arbitrary directives that are executed by wg-quick with root privileges. An attacker with clients.create permission achieves root code execution on the host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72603.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72603
- https://github.com/wg-easy/wg-easy
