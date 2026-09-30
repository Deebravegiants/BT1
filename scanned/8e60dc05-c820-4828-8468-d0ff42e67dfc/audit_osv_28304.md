# [M] Saleor CSRF bypass in refreshToken mutation

## Summary
Severity: Medium
Advisory: CVE-2024-31205
Aliases: GHSA-ff69-fwjf-3c9w
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-31205
Type: osv

## Details
Saleor is an e-commerce platform. Starting in version 3.10.0 and prior to versions 3.14.64, 3.15.39, 3.16.39, 3.17.35, 3.18.31, and 3.19.19, an attacker may bypass cross-set request forgery (CSRF) validation when calling refresh token mutation with empty string. When a user provides an empty string in `refreshToken` mutation, while the token persists in `JWT_REFRESH_TOKEN_COOKIE_NAME` cookie, application omits validation against CSRF token and returns valid access token. Versions 3.14.64, 3.15.39, 3.16.39, 3.17.35, 3.18.31, and 3.19.19 contain a patch for the issue. As a workaround, one may replace `saleor.graphql.account.mutations.authentication.refresh_token.py.get_refresh_token`. This will fix the issue, but be aware, that it returns `JWT_MISSING_TOKEN` instead of `JWT_INVALID_TOKEN`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31205.json
- https://github.com/saleor/saleor/security/advisories/GHSA-ff69-fwjf-3c9w
- https://nvd.nist.gov/vuln/detail/CVE-2024-31205
- https://github.com/saleor/saleor/commit/36699c6f5c99590d24f46e3d5c5b1a3c2fd072e7
