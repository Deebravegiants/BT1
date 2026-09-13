# [C] AVideo through 29.0 OS Command Injection via listFFmpegProcesses

## Summary
Severity: Critical
Advisory: CVE-2026-63304
Aliases: GHSA-j44m-77cc-p3cc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63304
Type: osv

## Details
AVideo through 29.0 contains an OS command injection vulnerability in plugin/API/standAlone/functions.php where the listFFmpegProcesses() function interpolates unsanitized keyword parameters inside single quotes without escaping. Attackers who can craft a valid encrypted codeToExec payload can break out of the single-quoted grep context and execute arbitrary OS commands as the web-server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63304.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-j44m-77cc-p3cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-63304
- https://www.vulncheck.com/advisories/avideo-through-os-command-injection-via-listffmpegprocesses
