# [H] SigNoz < 0.134.0 SSO OAuth State Manipulation Session Token Theft

## Summary
Severity: High
Advisory: CVE-2026-63094
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-63094
Type: osv

## Details
SigNoz before 0.134.0 contains an open redirect vulnerability in the SSO authentication flow that allows unauthenticated attackers to steal session tokens from any user on instances configured with Google OAuth, SAML, or OIDC. Attackers can call the unauthenticated sessions context endpoint with a ref parameter pointing to an attacker-controlled host, deliver the resulting crafted login URL to a victim, and receive the victim's access and refresh tokens when they complete SSO authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63094.json
- https://github.com/SigNoz/signoz/releases/tag/v0.134.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-63094
- https://www.vulncheck.com/advisories/signoz-sso-oauth-state-manipulation-session-token-theft
- https://github.com/SigNoz/signoz/pull/12172
- https://github.com/SigNoz/signoz/commit/253ca7dd7eb4f7a32a694c249eb0d5d0804d5619
- https://github.com/SigNoz/signoz
- https://github.com/SigNoz/signoz/issues/11746
