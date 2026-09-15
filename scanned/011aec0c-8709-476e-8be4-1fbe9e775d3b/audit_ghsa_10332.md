# [H] Heimdall: Case-sensitive handling of URL-encoded slashes may lead to inconsistent path interpretation

## Summary
Severity: High
Advisory: GHSA-43jv-5j4x-qv67
CVE: CVE-2026-42272
CWE: CWE-178, CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-43jv-5j4x-qv67
Type: github-advisory

## Affected
- Go: `github.com/dadrus/heimdall` — affected >=0 <0.17.14

## Details
### Summary

Heimdall handles URL-encoded slashes (`%2F`) in a case-sensitive manner, while percent-encoding is defined to be case-insensitive. As a result, the lowercase equivalent (`%2f`) is not recognized and therefore not processed as expected when `allow_encoded_slashes` is set to `off` (the default setting).

This discrepancy can lead to differences in how request paths are interpreted by heimdall and upstream components, which may result in authorization bypass.

**Note:** The issue can only lead to unintended access if heimdall is configured with an "allow all" default rule. Since v0.16.0, heimdall enforces secure defaults and refuses to start with such a configuration unless this enforcement is explicitly disabled (e.g. via `--insecure-skip-secure-default-rule-enforcement` or the broader `--insecure` flag).

### Details

Consider the following rule configuration:

```yaml
id: rule-1
match:
  routes:
    - path: /admin/**
execute: # configured to require authentication and authorization
  # ...
```

If an adversary sends a request such as `/admin%2fsecret`, neither is the above rule matched, nor is the request rejected (as would be expected when `allow_encoded_slashes` is set to `off`). Instead, the default rule (if configured) will be executed.

If the configured default rule is overly permissive (e.g. allowing anonymous access), and the upstream service interprets `%2f` as a path separator, the request may ultimately be processed as `/admin/secret`.

This results in the request being authorized based on a different path than the one processed by the upstream service, leading to authorization bypass.

### Impact

Bypass of access control policies enforced by heimdall may lead to the following consequences:

* Access to or modification of data that should be restricted
* Invocation of functionality that is expected to require authentication or authorization
* In certain configurations, escalation of privileges depending on the exposed functionality


### Workarounds

* Developers should not use the `--insecure` or the `--insecure-skip-secure-default-rule-enforcement` flags and configure their default rule to implement "deny by default".
* Reject HTTP paths containing encoded slashes in the layers in front of heimdall. Some proxies, like e.g., Traefik, do that by default.
* Include the ID of the rule expected to be executed in the JWT issued by heimdall and verify that value in the project's service.

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-43jv-5j4x-qv67
- https://nvd.nist.gov/vuln/detail/CVE-2026-42272
- https://github.com/dadrus/heimdall/pull/3207
- https://github.com/dadrus/heimdall/commit/8b0de6aba23a047cfee3081df878271bb17f4351
- https://github.com/dadrus/heimdall
- https://github.com/dadrus/heimdall/releases/tag/v0.17.14
