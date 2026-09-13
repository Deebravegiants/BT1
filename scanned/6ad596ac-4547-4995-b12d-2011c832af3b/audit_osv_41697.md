# [C] AVideo through 29.0 OS Command Injection via ffmpeg.json.php

## Summary
Severity: Critical
Advisory: CVE-2026-63305
Aliases: GHSA-g9x9-q7qj-6mv5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63305
Type: osv

## Details
AVideo through 29.0 contains an OS command injection vulnerability in the ffmpeg.json.php endpoint where notifyCode and callback parameters are concatenated into a shell command without escaping. Attackers who can craft a valid encrypted payload can inject arbitrary shell metacharacters into these fields to execute OS commands as the web-server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63305.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-g9x9-q7qj-6mv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-63305
- https://www.vulncheck.com/advisories/avideo-through-os-command-injection-via-ffmpeg-json-php
