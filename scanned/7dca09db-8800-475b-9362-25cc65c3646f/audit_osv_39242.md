# [M] Chatwoot: Pre-Account Takeover via OAuth on Unconfirmed Accounts

## Summary
Severity: Medium
Advisory: CVE-2026-44707
Aliases: GHSA-8qxm-4p4p-cfhm
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44707
Type: osv

## Details
Chatwoot is a customer engagement suite. From 2.14.0 to before 4.13.0, a Pre-Account Takeover (Pre-ATO) vulnerability existed in Chatwoot's authentication flow. Because email confirmation was not enforced before an account became usable, an attacker could pre-register an email address they did not own and set a password. If the legitimate owner of that email later signed in to Chatwoot using Google OAuth (or another OmniAuth provider), the OAuth flow silently confirmed the existing account without invalidating the attacker's pre-set credentials. The attacker could then continue to log in with the password they had originally chosen and access any data the victim subsequently entered into the dashboard, including PII, API keys, and other sensitive information. This vulnerability is fixed in 4.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44707.json
- https://github.com/chatwoot/chatwoot/security/advisories/GHSA-8qxm-4p4p-cfhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44707
- https://github.com/chatwoot/chatwoot/commit/211fb1102dd208daee414cff1b8d71ea27ac5ebf
- https://github.com/chatwoot/chatwoot/pull/13878
