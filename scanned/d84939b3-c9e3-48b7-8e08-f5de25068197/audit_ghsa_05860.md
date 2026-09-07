# [H] Statamic: Account takeover via OAuth email matching without email-verification check

## Summary
Severity: High
Advisory: GHSA-93qh-5269-9wcf
CVE: CVE-2026-64665
CWE: CWE-287, CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-93qh-5269-9wcf
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.1
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.0

## Details
### Impact

When OAuth login is enabled with a provider that does not guarantee verified email addresses, an unauthenticated attacker could sign in as an existing user — potentially including a super admin — without their password. Exploitation requires OAuth to be explicitly enabled with such a provider.

### Patches

Fixed in 5.74.1 and 6.24.0.

### Workarounds

Only enable OAuth with providers that guarantee verified email addresses, or disable OAuth login.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-93qh-5269-9wcf
- https://github.com/statamic/cms/pull/14887
- https://github.com/statamic/cms/commit/e59dd342c83bc45de26573cfb0536a0bca98255a
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.74.1
- https://github.com/statamic/cms/releases/tag/v6.24.0
