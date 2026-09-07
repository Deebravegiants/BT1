# [H] Zen Cart vulnerable to authenticated remote code execution

## Summary
Severity: High
Advisory: GHSA-38f9-4vhq-9cr8
CVE: CVE-2021-3291
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-38f9-4vhq-9cr8
Type: github-advisory

## Affected
- Packagist: `zencart/zencart` — affected >=0 <1.5.7c

## Details
Zen Cart 1.5.7b allows admins to execute arbitrary OS commands by inspecting an HTML radio input element (within the modules edit page) and inserting a command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3291
- https://github.com/zencart/zencart/commit/7447627f7148b11c614f89dab4a09d3f102b58af
- https://github.com/MucahitSaratar/zencart_auth_rce_poc
- https://github.com/zencart/zencart
- http://packetstormsecurity.com/files/161613/Zen-Cart-1.5.7b-Remote-Code-Execution.html
