# [H] ipl/web is vulnerable to reflected XSS by malformed search requests

## Summary
Severity: High
Advisory: GHSA-55wf-5m3q-6jjf
CVE: CVE-2026-42224
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-55wf-5m3q-6jjf
Type: github-advisory

## Affected
- Packagist: `ipl/web` — affected >=0.11.0 <0.13.1
- Packagist: `ipl/web` — affected >=0 <0.10.3

## Details
### Impact
The vulnerability allows an attacker to inject malicious Javascript into a victim's browser to run it in the context of Icinga Web. The victim needs to visit a specifically prepared website and may have no immediate chance to notice any wrongdoing.

### Patches
Version 0.13.1 includes a fix for this. It will be published as part of `icinga-php-library` version 0.19.2.

### Workarounds
Enable the Content-Security-Policy (CSP) in the general configuration of Icinga Web available since version 2.12.0.

### References
None

## References
- https://github.com/Icinga/ipl-web/security/advisories/GHSA-55wf-5m3q-6jjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-42224
- https://github.com/Icinga/ipl-web/commit/f387e92504d7a03bb857d1aee9b7410e06dd065d
- https://github.com/Icinga/ipl-web
- https://github.com/Icinga/ipl-web/releases/tag/v0.10.3
- https://github.com/Icinga/ipl-web/releases/tag/v0.13.1
