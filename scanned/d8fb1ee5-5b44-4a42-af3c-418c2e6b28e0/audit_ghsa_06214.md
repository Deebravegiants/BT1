# [M] Statamic: Stored Cross-Site Scripting in Automagic Form Notification Email Template

## Summary
Severity: Medium
Advisory: GHSA-vx89-p3j7-8xqc
CVE: CVE-2026-71435
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-vx89-p3j7-8xqc
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.3
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.2

## Details
### Impact

The default ("automagic") form notification email rendered user-submitted values without escaping, allowing an unauthenticated form submitter to inject HTML into the notification emails sent to the configured recipients

### Patches

This has been fixed in 5.74.3 and 6.24.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-vx89-p3j7-8xqc
- https://github.com/statamic/cms/pull/14959
- https://github.com/statamic/cms/commit/4ad1335e818a67249d0617f0f167a1198fb96a2c
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.74.3
- https://github.com/statamic/cms/releases/tag/v6.24.2
