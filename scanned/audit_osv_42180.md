# [C] ICEcoder through 8.1 OS Command Injection via lib/properties.php

## Summary
Severity: Critical
Advisory: CVE-2026-64837
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-64837
Type: osv

## Details
ICEcoder through 8.1 passes an unescaped filesystem path into a shell command in lib/properties.php, allowing authenticated users to inject OS commands through directory names. Attackers can create directories with shell metacharacters in their names and access the Properties function to execute arbitrary commands as the web-server user via popen().

## References
- https://packagist.org/packages/icecoder/icecoder
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64837.json
- https://github.com/Caycon/cve-advisories/blob/main/2026/ICEcoder/CVE-2026-64837.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-64837
- https://www.vulncheck.com/advisories/icecoder-through-8.1-os-command-injection-via-lib-properties-php
- https://github.com/icecoder/ICEcoder
- https://github.com/icecoder/ICEcoder/blob/4a61847ef7bb0360735cf1d55c45e5de9746e24e/lib/properties.php#L37
