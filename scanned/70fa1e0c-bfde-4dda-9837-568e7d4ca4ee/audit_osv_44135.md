# [H] better-auth SSO before 1.6.27 Domain Ownership Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-80192
Aliases: GHSA-8c5h-wx78-2cfg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80192
Type: osv

## Details
@better-auth/sso before 1.6.27 (and before 1.4.8 in the 1.4.x line and before 1.7.0-rc.5 in the 1.7 prerelease line) contains two domain-ownership flaws. When domain verification is disabled, automatic organization assignment accepts unverified provider domains, allowing an authenticated organization owner/administrator to register an SSO provider for an arbitrary domain and have users with matching email domains added to the attacker's organization with default member permissions. When domain verification is enabled, a race condition between the verify-domain and update-provider endpoints can apply completed DNS proof to a different domain; combined with implicit account linking, this can link an attacker-controlled identity provider to an existing user account. Exploitation requires the SSO plugin (and, for the org-assignment path, the organization plugin) with the relevant configuration enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80192.json
- https://github.com/better-auth/better-auth/security/advisories/GHSA-8c5h-wx78-2cfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-80192
- https://www.vulncheck.com/advisories/better-auth-sso-before-1.6.27-domain-ownership-authentication-bypass
