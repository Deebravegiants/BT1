# [M] authentik's invitation expiry is delayed by at least 5 minutes

## Summary
Severity: Medium
Advisory: GHSA-ch7q-53v8-73pc
CVE: CVE-2025-64708
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-ch7q-53v8-73pc
Type: github-advisory

## Affected
- Go: `goauthentik.io` — affected >=0 <0.0.0-20251119135424-6672e6aaa41e

## Details
### Summary

In previous authentik versions, invitations were considered valid regardless if they are expired or not, thus relying on background tasks to clean up expired ones. In a normal scenario this can take up to 5 minutes because the cleanup of expired objects is scheduled to run every 5 minutes. However, with a large amount of tasks in the backlog, this might take longer.

### Patches

authentik 2025.8.5 and 2025.10.2 fix this issue; for other versions the workaround below can be used.

### Workarounds

Users can create a policy that explicitly checks whether the invitation is still valid, and then bind it to the invitation stage on your invitation flow, and deny access if the invitation is not valid.

```python
return not context['flow_plan'].context['invitation'].is_expired
```

### For more information

If users have any questions or comments about this advisory:

- Email the authentik team at [security@goauthentik.io](mailto:security@goauthentik.io).

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-ch7q-53v8-73pc
- https://nvd.nist.gov/vuln/detail/CVE-2025-64708
- https://github.com/goauthentik/authentik/commit/6672e6aaa41e0f2c9bfb1e4d8b51cf114969e830
- https://github.com/goauthentik/authentik
