# [C] Portainer missing authorization on Docker plugin endpoints, which allows host RCE

## Summary
Severity: Critical
Advisory: GHSA-rrmm-9v76-h3p4
CVE: CVE-2026-44848
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rrmm-9v76-h3p4
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.2
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.41.0

## Details
## Summary

Portainer enforces Role-Based Access Control (RBAC) on top of the Docker API. The proxy layer routes incoming Docker API requests to per-resource handlers (containers, images, services, volumes, etc.) that apply authorization checks.

The Docker plugin management endpoints (`/plugins/*`) were not registered with a handler, so standard users with endpoint access could call privileged plugin operations — including installing and enabling plugins — directly against the underlying Docker daemon.

The vulnerability is exposed when a non-admin Portainer user (Standard User role, or any role granted endpoint-level access) has been given access to a Docker endpoint via Portainer RBAC. Administrators and users without Docker endpoint access are not affected.

A regular user with access to a Docker endpoint can:

- Pull an arbitrary plugin from any registry via `POST /plugins/pull`.
- Grant it the privileges it requests, including `CAP_SYS_ADMIN` and host-path mounts.
- Enable the plugin via `POST /plugins/{name}/enable`, at which point Docker runs the plugin with root privileges on the host.

Docker plugins execute as root on the host and can request arbitrary host capabilities and mounts. Enabling a crafted plugin gives the user access to the host filesystem and equivalent to root on the Docker host.

## Severity

**Critical** — CVSS 9.4
`CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H`

**CWE-862** — Missing Authorization

## Affected Versions

The vulnerability exists in every Portainer release where the Docker API proxy uses the prefix-allowlist routing model — `/plugins` has never been in the allowlist, and the fall-through path has never applied authorization.

Fixes are included in the next release of each supported branch:

| Branch              | First vulnerable | Fixed in   |
|---------------------|------------------|------------|
| 2.33.x (LTS)        | 2.33.0           | **2.33.8** |
| 2.39.x (LTS)        | 2.39.0           | **2.39.2** |
| 2.40.x (STS)        | 2.40.0           | **2.41.0** |

Portainer LTS branches receive fixes for 6 months plus a 3-month overlap after the next LTS ships. STS releases are supported only until the next STS ships — the 2.40.x STS line ends with the 2.41.0 release. All releases **prior to 2.33.0 are end-of-life** and will not receive a fix; users on EOL versions should upgrade to a supported LTS branch.

## Workarounds

Administrators who cannot immediately upgrade can reduce exposure by temporarily **revoking Docker endpoint access for non-admin users** via Portainer RBAC until the patched release is deployed. This eliminates the attack surface without disruption for administrators. This does not replace the fix.

## Affected Code

```go
// api/http/proxy/factory/docker/transport.go (pre-fix)

var prefixProxyFuncMap = map[string]func(...){
    "build":      ...,
    "configs":    ...,
    "containers": ...,
    "images":     ...,
    "networks":   ...,
    "nodes":      ...,
    "secrets":    ...,
    "services":   ...,
    "swarm":      ...,
    "tasks":      ...,
    "v2":         ...,
    "volumes":    ...,
}

func (transport *Transport) ProxyDockerRequest(request *http.Request) (*http.Response, error) {
    // ...
    prefix := strings.Split(strings.TrimPrefix(unversionedPath, "/"), "/")[0]

    if proxyFunc := prefixProxyFuncMap[prefix]; proxyFunc != nil {
        return proxyFunc(transport, request, unversionedPath)  // authorized
    }

    return transport.executeDockerRequest(request)  // forwarded without authorization
}
```

`/plugins` is not in `prefixProxyFuncMap`, so requests to plugin endpoints fall through to `executeDockerRequest` and are forwarded to the Docker daemon without any Portainer-side authorization check.


## Impact

An authenticated, non-admin Portainer user with access to any Docker-enabled endpoint can:

- Install and enable arbitrary Docker plugins from any registry.
- Execute plugin code with root privileges on the Docker host (including declaring `CAP_SYS_ADMIN` and host-path mounts).
- Read and modify files on the host filesystem from a restricted account, overriding the administrator's security policy.

## Timeline

- 2026-03-16: Reported via GitHub Security Advisory by **ikkebr**.
- 2026-04-20: Fix merged to `develop`, `release/2.39`, and `release/2.33`.
- 2026-04-29: 2.41.0 released.
- 2026-05-07: 2.39.2-LTS and 2.33.8-LTS released.

## Credit

- **ikkebr** — identified and reported the proxy allowlist bypass affecting the Docker plugin management endpoints.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-rrmm-9v76-h3p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44848
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
- https://github.com/portainer/portainer/releases/tag/2.41.0
