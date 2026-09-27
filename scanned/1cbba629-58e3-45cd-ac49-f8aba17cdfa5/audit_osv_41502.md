# [H] Wallos: OIDC account takeover via email-based account linking without `email_verified` check

## Summary
Severity: High
Advisory: CVE-2026-61641
Aliases: GHSA-qwgp-m2f3-6j3r
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-61641
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. From version 4.0.0 to before version 4.9.6, Wallos's OIDC login links an incoming OIDC identity to an existing local account by matching the email claim alone, without verifying that the IdP marked that email as verified (email_verified). When Wallos is configured against an IdP that lets a user present an arbitrary or unverified email (multi-tenant IdPs, IdPs with open self-registration, or any IdP the attacker partly controls), an attacker with no Wallos account can authenticate with the admin's email and be logged in as the admin — full account takeover, no password needed. This issue has been patched in version 4.9.6.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61641.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-qwgp-m2f3-6j3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-61641
- https://github.com/ellite/Wallos/commit/b75f13d0ffa3ed7e77e8e79e4b9fd3fc528c98d3
- https://github.com/ellite/Wallos/pull/1092
