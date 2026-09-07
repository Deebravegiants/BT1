# [M] October Rain has Stored XSS via SVG Filter Bypass

## Summary
Severity: Medium
Advisory: GHSA-gcqv-f29m-67gr
CVE: CVE-2026-25133
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gcqv-f29m-67gr
Type: github-advisory

## Affected
- Packagist: `october/rain` — affected >=4.0.0 <4.1.10
- Packagist: `october/rain` — affected >=0 <3.7.14

## Details
A stored cross-site scripting (XSS) vulnerability was identified in the SVG sanitization logic. The regex pattern used to strip `on*` event handler attributes could be bypassed using a crafted payload that exploits how the pattern matches attribute boundaries.

### Impact
- Stored XSS via malicious SVG files uploaded through the Media Manager
- Could allow privilege escalation if a superuser views or embeds the malicious SVG
- Requires authenticated backend access with media upload permissions (`media.library.create`)
- SVG must be viewed or embedded in a page to trigger

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Disable SVG uploads by adding `svg` to the blocked extensions in media configuration
- Set `media.clean_vectors` to `true` in configuration (enabled by default)

### References
- Reported by Pentest-Tools.com

## References
- https://github.com/octobercms/october/security/advisories/GHSA-gcqv-f29m-67gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25133
- https://github.com/octobercms/october
