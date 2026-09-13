# [M] Caido Improperly Handles External Links in Markdown

## Summary
Severity: Medium
Advisory: CVE-2025-66025
Aliases: GHSA-cf52-h5mw-gmc2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-66025
Type: osv

## Details
Caido is a web security auditing toolkit. Prior to version 0.53.0, the Markdown renderer used in Caido’s Findings page improperly handled user-supplied Markdown, allowing attacker-controlled links to be rendered without confirmation. When a user opened a finding generated through the scanner, or other plugins, clicking these injected links could redirect the Caido application to an attacker-controlled domain, enabling phishing style attacks. This issue has been patched in version 0.53.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66025.json
- https://github.com/caido/caido/security/advisories/GHSA-cf52-h5mw-gmc2
- https://nvd.nist.gov/vuln/detail/CVE-2025-66025
