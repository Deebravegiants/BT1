# [C] Coolify through 4.3.17 OAuth Account Takeover via Unverified Email Matching

## Summary
Severity: Critical
Advisory: CVE-2026-86117
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86117
Type: osv

## Details
Coolify through 4.3.17 contains an authentication bypass vulnerability in the OAuth callback handler that signs users into existing accounts based solely on email address without verifying provider assertions or binding OAuth identities. Attackers can register a victim's email address on any enabled OAuth provider to obtain authenticated sessions as that user, bypassing password requirements and two-factor authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86117
- https://www.vulncheck.com/advisories/coolify-through-4.3.17-oauth-account-takeover-via-unverified-email-matching
- https://github.com/coollabsio/coolify
- https://github.com/coollabsio/coolify/blob/v4.3.17/app/Http/Controllers/OauthController.php
- https://github.com/coollabsio/coolify/blob/v4.3.17/routes/web.php
- https://github.com/geo-chen/oss/blob/main/coolify.md
