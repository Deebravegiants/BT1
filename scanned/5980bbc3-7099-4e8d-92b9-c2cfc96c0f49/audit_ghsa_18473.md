# [H] Authentik has insufficient check for account active status when authenticating with OAuth/SAML Sources

## Summary
Severity: High
Advisory: GHSA-9g4j-v8w5-7x42
CVE: CVE-2025-53942
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-07-22
Source: https://github.com/advisories/GHSA-9g4j-v8w5-7x42
Type: github-advisory

## Affected
- Go: `goauthentik.io` — affected >=0 <0.0.0-20250722122105-7a4c6b9b50f8

## Details
### Summary

Deactivated users that had either enrolled via OAuth/SAML or had their account connected to an OAuth/SAML account can still partially access authentik even if their account is deactivated. They end up in a half-authenticated state where they cannot access the API but crucially they can authorize applications if they know the URL of the application.

### Patches

authentik 2025.4.4 and 2025.6.4 fix this issue.

### Workarounds

Adding an expression policy to the user login stage on the respective authentication flow with the expression of

```py
return request.context["pending_user"].is_active
```

This expression will only activate the user login stage when the user is active.

### For more information

If you have any questions or comments about this advisory:

- Email us at [security@goauthentik.io](mailto:security@goauthentik.io).

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-9g4j-v8w5-7x42
- https://nvd.nist.gov/vuln/detail/CVE-2025-53942
- https://github.com/goauthentik/authentik/commit/7a4c6b9b50f8b837133a7a1fd2cb9b7f18a145cd
- https://github.com/goauthentik/authentik/commit/c3629d12bfe3d32d3dc8f85c0ee1f087a55dde8f
- https://github.com/goauthentik/authentik/commit/ce3f9e3763c1778bf3a16b98c95d10f4091436ab
- https://github.com/goauthentik/authentik
