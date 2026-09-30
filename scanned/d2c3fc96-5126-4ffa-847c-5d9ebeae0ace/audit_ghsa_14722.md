# [M] kcp's impersonation allows access to global administrative groups

## Summary
Severity: Medium
Advisory: GHSA-c7xh-gjv4-4jgv
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-c7xh-gjv4-4jgv
Type: github-advisory

## Affected
- Go: `github.com/kcp-dev/kcp` — affected >=0 <0.26.1

## Details
### Impact

[Impersonation](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#user-impersonation) is a feature of the Kubernetes API, allowing to override user information. As downstream project, kcp inherits this feature. As per the linked documentation a specific level of privilege (usually assigned to cluster admins) is required for impersonation.

The vulnerability in kcp affects kcp installations in which users are granted the `cluster-admin` ClusterRole (or comparably high permission levels that grant impersonation access; the verb in question is `impersonate`) within their respective workspaces. As kcp builds around self-service confined within workspaces, most installations would likely grant such workspace access to their users. Such users can impersonate special global administrative groups, which circumvent parts of the authorizer chains, e.g. [maximal permission policies](https://docs.kcp.io/kcp/v0.26/concepts/apis/exporting-apis/#maximal-permission-policy).

### Patches

The problem has been patched in #3206 and is available in kcp 0.26.1 and higher.

### Workarounds

- Not assigning the `cluster-admin` role (or any other role granting blanket impersonation permissions) to users.
- A reverse proxy between users and kcp to check for the `Impersonate-Group` header and reject requests that impersonate global administrative groups.

### References

See the pull request (#3206).

## References
- https://github.com/kcp-dev/kcp/security/advisories/GHSA-c7xh-gjv4-4jgv
- https://github.com/kcp-dev/kcp/pull/3206
- https://github.com/kcp-dev/kcp/commit/24ab5d4dc35ddff98a2e5fdc236e1681f03283ec
- https://github.com/kcp-dev/kcp
- https://pkg.go.dev/vuln/GO-2024-3325
