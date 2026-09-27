# [H] Heimdall: Case-sensitive host matching may lead to policy bypass

## Summary
Severity: High
Advisory: GHSA-72h4-mxfc-jx37
CVE: CVE-2026-42273
CWE: CWE-178, CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-72h4-mxfc-jx37
Type: github-advisory

## Affected
- Go: `github.com/dadrus/heimdall` — affected >=0 <0.17.14

## Details
### Summary

Heimdall performs host matching in a case-sensitive manner, while HTTP hostnames are case-insensitive. This discrepancy can result in heimdall failing to match a rule for a request host that differs only in letter casing, potentially causing the request to be classified differently than intended.

**Note:** The issue can only lead to unintended access if heimdall is configured with an "allow all" default rule. Since v0.16.0, heimdall enforces secure defaults and refuses to start with such a configuration unless this enforcement is explicitly disabled, e.g. via `--insecure-skip-secure-default-rule-enforcement` or the broader `--insecure` flag.

### Details

This vulnerability can potentially be exploited by an adversary if rule matching relies on the request host.

For example, consider the following rule:

```yaml
id: rule-1
match:
  hosts:
    - type: exact
      value: admin.example.com
execute: # configured to require authentication and authorization
  # ...
```

If an adversary now sends a request with the `Host` header set to `Admin.Example.Com`, rule-1 will not be matched, and the following will happen instead:

* If no default rule is configured, the request will result in an error (`404 Not Found`)
* If a default rule is configured, it will be executed. If the default rule is configured in an overly permissive way (e.g. allowing anonymous access), this results in a policy bypass.

### Impact

Bypass of access control policies enforced by heimdall may lead to the following consequences:

* Access to or modification of data that should be restricted
* Invocation of functionality that is expected to require authentication or authorization
* In certain configurations, escalation of privileges depending on the exposed functionality

### Workarounds

* Normalize request hosts to lowercase in the layers in front of heimdall.
* Do not configure a permissive default rule. Respectively, do not make use of the `--insecure` or the `--insecure-skip-secure-default-rule-enforcement` flags.
* When using `regex` type for host matching, expressions shall be defined in a case-insensitive manner (e.g. `(?i)^admin\.example\.com$`)
* Include the ID of the rule expected to be executed in the JWT issued by heimdall and check that value in the consuming project's service.

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-72h4-mxfc-jx37
- https://nvd.nist.gov/vuln/detail/CVE-2026-42273
- https://github.com/dadrus/heimdall/pull/3208
- https://github.com/dadrus/heimdall/commit/3d05e56a9e7ef0355f17482b4322054af4e85943
- https://github.com/dadrus/heimdall
- https://github.com/dadrus/heimdall/releases/tag/v0.17.14
