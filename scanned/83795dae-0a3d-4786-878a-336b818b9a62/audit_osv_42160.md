# [C] FreeRDP RDP File Parser Remote Code Execution via CLI Options

## Summary
Severity: Critical
Advisory: CVE-2026-64624
Aliases: GHSA-rq8f-9xjh-pr3m
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64624
Type: osv

## Details
FreeRDP before 3.28.0 treats lines beginning with forward slash in RDP files as raw command-line options, exposing the entire CLI parser surface to untrusted files. Attackers can craft malicious RDP files with /rdp2tcp, /cert:ignore, or /drive options to execute arbitrary commands, bypass certificate validation, or expose local filesystems without user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64624.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-rq8f-9xjh-pr3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-64624
- https://www.vulncheck.com/advisories/freerdp-rdp-file-parser-remote-code-execution-via-cli-options
