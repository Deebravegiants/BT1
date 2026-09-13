# [C] Combodo iTop vulnerable to Remote Code Execution in the backup creation functionality

## Summary
Severity: Critical
Advisory: CVE-2025-47286
Aliases: GHSA-4w93-rw6g-5m9c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-47286
Type: osv

## Details
Combodo iTop is a web based IT service management tool. In versions prior to 2.7.13 and 3.2.2, an administrator can, by editing the configuration of the iTop instance, execute code on the server. Versions 2.7.13 and 3.2.2 escape and check the config parameter before executing a command based on it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47286.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-4w93-rw6g-5m9c
- https://nvd.nist.gov/vuln/detail/CVE-2025-47286
