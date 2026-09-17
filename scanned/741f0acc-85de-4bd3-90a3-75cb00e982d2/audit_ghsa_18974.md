# [M] authentik allows a deactivated Service account to authenticate to OAuth

## Summary
Severity: Medium
Advisory: GHSA-xr73-jq5p-ch8r
CVE: CVE-2025-64521
CWE: CWE-286, CWE-289
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-xr73-jq5p-ch8r
Type: github-advisory

## Affected
- Go: `goauthentik.io` — affected >=0 <0.0.0-20251119140106-9dbdfc3f1be0

## Details
### Summary

When authenticating with `client_id` and `client_secret` to an OAuth provider, authentik creates a service account for the provider. In previous authentik versions, authentication for this account was possible even when the account was deactivated. Other permissions are correctly applied and federation with other providers still take assigned policies correctly into account.

### Patches

authentik 2025.8.5 and 2025.10.2 fix this issue, for other versions the workaround below can be used.

### Workarounds

You can add a policy to your application that explicitly checks if the service account is still valid, and deny access if not.

```python
return request.user.is_active
```

### For more information

If you have any questions or comments about this advisory:

- Email us at [security@goauthentik.io](mailto:security@goauthentik.io).

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-xr73-jq5p-ch8r
- https://nvd.nist.gov/vuln/detail/CVE-2025-64521
- https://github.com/goauthentik/authentik/commit/9dbdfc3f1be0f1be36f8efce2442897b2a54a71c
- https://github.com/goauthentik/authentik
