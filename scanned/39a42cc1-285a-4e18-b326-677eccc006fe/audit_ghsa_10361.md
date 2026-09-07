# [M] ProcessWire: server-side request forgery vulnerability in the admin panel's 'Add Module From URL' feature

## Summary
Severity: Medium
Advisory: GHSA-gmwr-9j4p-96vm
CVE: CVE-2026-40500
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-gmwr-9j4p-96vm
Type: github-advisory

## Affected
- Packagist: `processwire/processwire` — affected >=0

## Details
ProcessWire CMS version 3.0.255 and prior contain a server-side request forgery vulnerability in the admin panel's 'Add Module From URL' feature that allows authenticated administrators to supply arbitrary URLs to the module download parameter, causing the server to issue outbound HTTP requests to attacker-controlled internal or external hosts. Attackers can exploit differentiable error messages returned by the server to perform reliable internal network port scanning, host enumeration across RFC-1918 ranges, and potential access to cloud instance metadata endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40500
- https://gist.github.com/thepiyushkumarshukla/7514e5eed526fd9d20fcfc42ce8d0a82
- https://github.com/processwire/processwire
- https://processwire.com
- https://www.vulncheck.com/advisories/processwire-cms-ssrf-via-add-module-from-url
