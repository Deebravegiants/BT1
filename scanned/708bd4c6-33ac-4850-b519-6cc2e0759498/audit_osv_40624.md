# [C] OTRS Community Edition OS Command Injection via PGP Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-53804
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-53804
Type: osv

## Details
OTRS Community Edition contains an authenticated OS command injection vulnerability in the PGP encryption module that allows administrators to execute arbitrary operating-system commands by supplying crafted values for the PGP binary path and command options. Administrator-supplied configuration values are concatenated without sanitization into a shell command, enabling arbitrary command execution as the web server process user during normal ticket operations after the malicious configuration is deployed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53804.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53804
- https://www.vulncheck.com/advisories/otrs-community-edition-os-command-injection-via-pgp-configuration
- https://github.com/Centuran/OTRS-Community-Edition
- https://h00die-gr3y.github.io/research/cve-2026-53804/
