# [M] capsule-proxy service discloses Namespaces of colliding tenants to owners of different tenants with the same ServiceAccount name

## Summary
Severity: Medium
Advisory: GHSA-6758-979h-249x
CVE: CVE-2023-46254
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-07
Source: https://github.com/advisories/GHSA-6758-979h-249x
Type: github-advisory

## Affected
- Go: `github.com/projectcapsule/capsule` — affected >=0 <0.4.5
- Go: `github.com/projectcapsule/capsule-proxy` — affected >=0 <0.4.5

## Details
### Summary

A bug in the RoleBinding reflector used by `capsule-proxy` gives ServiceAccount tenant owners the right to list Namespaces of other tenants backed by the same owner kind and name.

### Details

- Tenant `solar`, owned by a ServiceAccount named `tenant-owner` in the Namespace `solar`
- Tenant `wind`, owned by a ServiceAccount named `tenant-owner` in the Namespace `wind`

> Please, notice the same ServiceAccount name, although in different namespaces.

The Tenant owner `solar` would be able to list the namespaces of the Tenant `wind` and vice-versa, although this is not correct.

The bug introduces an exfiltration vulnerability since allows the listing of Namespace resources of other Tenants, although just in some specific conditions:

1. `capsule-proxy` runs with the `--disable-caching=false` (default value: `false`)
2. Tenant owners are ServiceAccount, with the same resource name, but in different Namespaces.

The CVE doesn't allow any privilege escalation on the outer tenant Namespace-scoped resources, since the Kubernetes RBAC is enforcing this.

## References
- https://github.com/projectcapsule/capsule-proxy/security/advisories/GHSA-6758-979h-249x
- https://nvd.nist.gov/vuln/detail/CVE-2023-46254
- https://github.com/projectcapsule/capsule-proxy/commit/615202f7b02eaec7681336bd63daed1f39ae00c5
- https://github.com/projectcapsule/capsule-proxy
- https://github.com/projectcapsule/capsule-proxy/releases/tag/v0.4.5
