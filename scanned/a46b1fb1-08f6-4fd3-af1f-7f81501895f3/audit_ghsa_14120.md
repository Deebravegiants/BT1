# [M] Ibexa User Settings are accessible on the front-end for anonymous user

## Summary
Severity: Medium
Advisory: GHSA-r3fg-3r88-6x3f
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-10
Source: https://github.com/advisories/GHSA-r3fg-3r88-6x3f
Type: github-advisory

## Affected
- Packagist: `ibexa/user` — affected >=4.0.0 <4.4.3

## Details
### Impact
This security advisory is about the user settings, which include things like preferred time zone and number of items per page in item listings. These could be accessed by the anonymous user. This impacted only the anonymous users themselves, and had no impact on logged in users. As such the impact is limited, even if custom user settings have been added, but please consider if this matters for your site. The fix ensures that only logged in users can access their user settings.

### References
https://developers.ibexa.co/security-advisories/ibexa-sa-2023-002-user-settings-are-accessible-on-the-front-end-for-the-anonymous-user

## References
- https://github.com/ibexa/user/security/advisories/GHSA-r3fg-3r88-6x3f
- https://github.com/ibexa/user/commit/77d1a0926d93ca85aa6faeea66bee55e0e067551
- https://developers.ibexa.co/security-advisories/ibexa-sa-2023-002-user-settings-are-accessible-on-the-front-end-for-the-anonymous-user
- https://github.com/ibexa/user
