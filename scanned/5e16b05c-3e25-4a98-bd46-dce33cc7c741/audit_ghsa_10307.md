# [H] Cockpit Vulnerable to Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-j2rx-4jg9-79mw
CVE: CVE-2026-38991
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-j2rx-4jg9-79mw
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.14.0

## Details
Cockpit versions 2.13.5 and earlier are affected by a misconfiguration within the Bucket component _isFileTypeAllowed function where a specially crafted filename bypasses an extension filter. This allows an authenticated attacker to rename arbitrary files with the .php file extension enabling arbitrary code to be executed on the underlying server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38991
- https://felsec.com/posts/cockpit-cms-2.13.5-multi-vulns
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.14.0
