# [C] openssl_encrypt before 1.4.9 Terminal Injection via info Command

## Summary
Severity: Critical
Advisory: CVE-2026-81696
Aliases: GHSA-539p-fxf4-7fv8, PYSEC-2026-3775
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81696
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to sanitize terminal control characters in file metadata printed by the info command. Attackers can craft malicious files containing escape sequences to repaint terminal output and forge verification information displayed to users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81696.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-539p-fxf4-7fv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-81696
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-terminal-injection-via-info-command
