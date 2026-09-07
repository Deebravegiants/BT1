# [C] toui allows user-specific variables to be shared between users

## Summary
Severity: Critical
Advisory: GHSA-hh7j-pg39-q563
CVE: CVE-2023-33175
CWE: CWE-913, CWE-914
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-hh7j-pg39-q563
Type: github-advisory

## Affected
- PyPI: `toui` — affected >=2.0.1 <2.4.1

## Details
### Impact
Websites that use `Website.user_vars` property in versions.

### Patches
It affects versions v2.0.1 to v2.4.0. Please upgrade to v2.4.1

### Workarounds
Do not use `Website.user_vars` in websites when using versions v2.0.1 to v2.4.0. Also, do not use `Website.signin_user()` in version v2.4.0 only.

### Explanation
ToUI is using Flask-Caching (SimpleCache) to store user variables. My misunderstanding was that these caches are stored in the client's browser, but it seems that these are stored in the server side.

## References
- https://github.com/mubarakalmehairbi/ToUI/security/advisories/GHSA-hh7j-pg39-q563
- https://nvd.nist.gov/vuln/detail/CVE-2023-33175
- https://github.com/mubarakalmehairbi/ToUI
- https://github.com/mubarakalmehairbi/ToUI/releases/tag/v2.4.1
