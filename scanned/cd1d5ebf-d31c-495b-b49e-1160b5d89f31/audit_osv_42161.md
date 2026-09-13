# [C] AVideo before 29.0 OS Command Injection via execAsync

## Summary
Severity: Critical
Advisory: CVE-2026-64625
Aliases: GHSA-rc5x-vh5v-473f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64625
Type: osv

## Details
AVideo before 29.0 contains an incomplete fix for CVE-2026-45578 where execAsync() re-wraps escaped commands in double-quoted sh -c, allowing command substitution via $() and backticks. Attackers can inject arbitrary OS commands through the Live plugin on_publish.php endpoint despite escapeshellarg() protection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64625.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-rc5x-vh5v-473f
- https://nvd.nist.gov/vuln/detail/CVE-2026-64625
- https://www.vulncheck.com/advisories/avideo-before-os-command-injection-via-execasync
