# [C] OPNsense: Command Injection via Attacker-Controlled DHCP Config

## Summary
Severity: Critical
Advisory: CVE-2026-45158
Aliases: GHSA-5rx3-w735-74wm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45158
Type: osv

## Details
OPNsense is a FreeBSD based firewall and routing platform. Prior to 26.1.8, unsanitized user input is passed to the DHCP configuration of the configured interface, which is processed by a shell script, allowing remote code execution as root on the underlying operating system. This vulnerability is fixed in 26.1.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45158.json
- https://github.com/opnsense/core/security/advisories/GHSA-5rx3-w735-74wm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45158
