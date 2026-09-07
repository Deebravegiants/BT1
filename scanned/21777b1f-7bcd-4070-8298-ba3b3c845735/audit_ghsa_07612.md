# [M] AVideo has Stored Cross-Site Scripting via Markdown Comment Injection

## Summary
Severity: Medium
Advisory: GHSA-rcqw-6466-3mv7
CVE: CVE-2026-27568
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-rcqw-6466-3mv7
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <21.0

## Details
## Vulnerability Type
Stored Cross-Site Scripting (XSS) — CWE-79.

## Affected Product/Versions
AVideo 18.0.

## Root Cause Summary
AVideo allows Markdown in video comments and uses Parsedown (v1.7.4) without Safe Mode enabled. Markdown links are not sufficiently sanitized, allowing `javascript:` URIs to be rendered as clickable links.

## Impact Summary
An authenticated low-privilege attacker can post a malicious comment that injects persistent JavaScript. When another user clicks the link, the attacker can perform actions such as session hijacking, privilege escalation (including admin takeover), and data exfiltration.

## Resolution/Fix
The issue was confirmed and fixed in the master branch. An official release will be published soon.

## Workarounds
Until the release is available, validate and block unsafe URI schemes (e.g., `javascript:`) before rendering Markdown, and enable Parsedown Safe Mode.

## Credits/Acknowledgement
Reported by Arkadiusz Marta (https://github.com/arkmarta/).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-rcqw-6466-3mv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27568
- https://github.com/WWBN/AVideo/commit/ade348ed6d28b3797162c3d9e98054fb09ec51d7
- https://github.com/WWBN/AVideo
- https://github.com/WWBN/AVideo/releases/tag/21.0
