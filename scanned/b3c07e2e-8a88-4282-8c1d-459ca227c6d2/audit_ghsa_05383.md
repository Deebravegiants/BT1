# [M] Flux Operator Web UI Impersonation Bypass via Empty OIDC Claims

## Summary
Severity: Medium
Advisory: GHSA-4xh5-jcj2-ch8q
CVE: CVE-2026-23990
CWE: CWE-269, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-4xh5-jcj2-ch8q
Type: github-advisory

## Affected
- Go: `github.com/controlplaneio-fluxcd/flux-operator` — affected >=0.36.0 <0.40.0

## Details
A privilege escalation vulnerability exists in the Flux Operator Web UI authentication code that allows an attacker to bypass Kubernetes RBAC impersonation and execute API requests with the operator's service account privileges.

After OIDC token claims are processed through CEL expressions, there is no validation that the resulting `username` and `groups` values are non-empty. When both values are empty, the Kubernetes client-go library does not add impersonation headers to API requests, causing them to be executed with the flux-operator service account's credentials instead of the authenticated user's limited permissions.

### Impact

- **Privilege Escalation**: Any authenticated user can escalate to operator-level read permissions and perform suspend/resume/reconcile actions
- **Data Exposure**: Unauthorized read access to Flux resources across all namespaces, bypassing RBAC restrictions
- **Information Disclosure**: View sensitive GitOps pipeline configurations, source URLs, and deployment status across the entire cluster

### Attack Scenario

**Prerequisite**: Cluster admins must configure the Flux Operator with an OIDC provider that issues tokens lacking the expected claims (e.g., `email`, `groups`), or configure custom CEL expressions that can evaluate to empty values.

1. Cluster admin configures OIDC authentication with a provider that does not include `email` or `groups` claims in tokens
2. User authenticates with a valid token from that provider
3. The default CEL expressions evaluate to empty values:
   - Username: `has(claims.email) ? claims.email : ''` → `""`
   - Groups: `has(claims.groups) ? claims.groups : []` → `[]`
4. Authentication succeeds (token signature is valid)
5. A userClient is created with empty impersonation config
6. All subsequent API requests bypass impersonation and execute as the flux-operator service account
7. User gains operator-level read access across all namespaces

### Patches

This vulnerability was fixed in Flux Operator v0.40.0.

### Workarounds

The workaround is to make the `email` and `groups` claims required in the web config `impersonation` section.

Example config:

```yaml
apiVersion: web.fluxcd.controlplane.io/v1
kind: Config
spec:
  baseURL: https://flux.example.com
  authentication:
    type: OAuth2
    oauth2:
      provider: OIDC
      clientID: "<redacted>"
      clientSecret: "<redacted>"
      issuerURL: "https://login.microsoftonline.com/<redacted>/v2.0"
      scopes: [openid, profile, email, offline_access]
      impersonation:
        username: claims.email
        groups: claims.groups
```

### References

See the Pull Request fixing this vulnerability https://github.com/controlplaneio-fluxcd/flux-operator/pull/610 

### Credits

This vulnerability was discovered by the Flux Operator maintainers during a debugging session with end-users.

## References
- https://github.com/controlplaneio-fluxcd/flux-operator/security/advisories/GHSA-4xh5-jcj2-ch8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-23990
- https://github.com/controlplaneio-fluxcd/flux-operator/pull/610
- https://github.com/controlplaneio-fluxcd/flux-operator/commit/084540424f6de8ba5d88fb1fd1e8472ba29afd7e
- https://github.com/controlplaneio-fluxcd/flux-operator
- https://github.com/controlplaneio-fluxcd/flux-operator/releases/tag/v0.40.0
