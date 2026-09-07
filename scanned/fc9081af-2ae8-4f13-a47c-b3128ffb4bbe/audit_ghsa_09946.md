# [M] October CMS has Stored XSS in Event Log Mail Preview

## Summary
Severity: Medium
Advisory: GHSA-j4j5-9x6g-rgxc
CVE: CVE-2026-24907
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-j4j5-9x6g-rgxc
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=4.0.0 <4.1.10
- Packagist: `october/system` — affected >=0 <3.7.14

## Details
A stored cross-site scripting (XSS) vulnerability was identified in the Event Log mail preview feature. When viewing logged mail messages, HTML content was rendered in an iframe without proper sandboxing, allowing JavaScript execution in the viewer's browser context.

### Impact
- Stored XSS via mail template content rendered in Event Log
- Could allow privilege escalation if a superuser views a malicious log entry
- Requires authenticated backend access with mail template editing permissions
- Requires a superuser to view the specific Event Log entry to trigger

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Restrict mail template editing permissions to fully trusted administrators only
- Restrict Event Log viewing permissions to minimize exposure

### References
- Reported by [Chris Alupului](https://github.com/neosprings)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-j4j5-9x6g-rgxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24907
- https://github.com/octobercms/october
