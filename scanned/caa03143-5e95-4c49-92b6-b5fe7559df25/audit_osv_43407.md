# [C] Laravel Socialite Facebook Provider Authentication Bypass via Nonce Replay

## Summary
Severity: Critical
Advisory: CVE-2026-73683
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73683
Type: osv

## Details
Laravel Socialite's Facebook provider contains an authentication bypass vulnerability that allows unauthenticated attackers to replay captured OIDC id_tokens by exploiting the missing nonce claim validation in the getUserByOIDCToken() function within FacebookProvider.php. Attackers who obtain a valid, unexpired id_token issued for the same Facebook App ID can submit the captured token to the backend userFromToken() endpoint, bypassing authentication controls because signature, aud, and iss checks pass while no session-bound nonce comparison is performed, resulting in unauthorized access to victim accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73683.json
- https://github.com/laravel/socialite
- https://nvd.nist.gov/vuln/detail/CVE-2026-73683
- https://www.vulncheck.com/advisories/laravel-socialite-facebook-provider-authentication-bypass-via-nonce-replay
- https://github.com/laravel/socialite/commit/caf714f55d51ab0d914b40033d8b0f489d6219cc
- https://github.com/laravel/socialite/pull/789
