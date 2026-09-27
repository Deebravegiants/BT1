# [H] CVE-2020-12078

## Summary
Severity: High
Advisory: CVE-2020-12078
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-12078
Type: osv

## Details
An issue was discovered in Open-AudIT 3.3.1. There is shell metacharacter injection via attributes to an open-audit/configuration/ URI. An attacker can exploit this by adding an excluded IP address to the global discovery settings (internally called exclude_ip). This exclude_ip value is passed to the exec function in the discoveries_helper.php file (inside the all_ip_list function) without being filtered, which means that the attacker can provide a payload instead of a valid IP address.

## References
- https://github.com/Opmantek/open-audit/commit/6ffc7f9032c55eaa1c37cf5e070809b7211c7e9a
- http://packetstormsecurity.com/files/157477/Open-AudIT-Professional-3.3.1-Remote-Code-Execution.html
- https://gist.github.com/mhaskar/dca62d0f0facc13f6364b8ed88d5a7fd
- https://shells.systems/open-audit-v3-3-1-remote-command-execution-cve-2020-12078/
