# [H] Socialstream has a Potential Account Takeover Vulnerability in Social Account Linking Due to Missing User Consent After OAuth Callback

## Summary
Severity: High
Advisory: GHSA-3q97-vjpp-c8rp
CVE: CVE-2024-56329
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-3q97-vjpp-c8rp
Type: github-advisory

## Affected
- Packagist: `joelbutcher/socialstream` — affected >=6.0.0 <6.2.0
- Packagist: `joelbutcher/socialstream` — affected >=0 <5.6.0

## Details
## Description

When linking a social account to an already authenticated user, the lack of a confirmation step introduces a security risk. This is exacerbated if ->stateless() is used in the Socialite configuration, bypassing state verification and making the exploit easier. Developers should ensure that users explicitly confirm account linking and avoid configurations that skip critical security checks.

## Resolution
Socialstream v6.2 introduces a new custom route that requires a user to "Confirm" or "Deny" a request to link a social account.

## References
- https://github.com/joelbutcher/socialstream/security/advisories/GHSA-3q97-vjpp-c8rp
- https://nvd.nist.gov/vuln/detail/CVE-2024-56329
- https://github.com/joelbutcher/socialstream/commit/ae4dc3906f54fa792b296036d7b3dcea9a4d259b
- https://github.com/joelbutcher/socialstream
