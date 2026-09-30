# [C] Portainer has an endpoint security bypass via Swarm service create/update

## Summary
Severity: Critical
Advisory: GHSA-5fxq-qcf3-244w
CVE: CVE-2026-44849
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-5fxq-qcf3-244w
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.2
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.41.0

## Details
## Summary

Portainer enforces seven `EndpointSecuritySettings` restrictions that administrators configure to restrict the container configurations non-admin users can launch: **privileged mode**, **host PID namespace**, **device mapping**, **capabilities**, **sysctls**, **security-opt (Seccomp / AppArmor)**, and **bind mounts**.

The vulnerability is exposed when a non-admin Portainer user (Standard User role, or any role granted endpoint-level access) has been given access to a Docker Swarm endpoint via Portainer RBAC. Admins and users without Swarm endpoint access are not affected.

These restrictions are enforced on the standard container creation path, but several of them are not applied on the Docker Swarm service API:

- `POST /services/create` — **1 of 7** checks applied. `CapabilityAdd`, `CapabilityDrop`, `Sysctls`, and `Privileges` (Seccomp / AppArmor) are not parsed from the request body and are forwarded to the Docker daemon without validation.
- `POST /services/{id}/update` — **0 of 7** checks applied. The route dispatches to the generic `restrictedResourceOperation`, which validates RBAC ownership but does not inspect the request body or call `fetchEndpointSecuritySettings()`.

The `EndpointSecuritySettings` checks apply when the administrator has configured any of `AllowContainerCapabilitiesForRegularUsers`, `AllowSysctlSettingForRegularUsers`, `AllowSecurityOptForRegularUsers`, or `AllowBindMountsForRegularUsers` to restrict standard users.

A regular user with access to a Docker Swarm endpoint can:

- Create a service with `CapabilityAdd: ["SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE", …]` or `Privileges.Seccomp.Mode: "unconfined"`.
- Create a benign service that passes ownership checks, then **update** it to add `CapabilityAdd: ["ALL"]` plus a bind mount of `/`, scale to one replica, and access the host filesystem from the running container (e.g. via `chroot /host`).

In addition, the partial `Mounts[]` struct used by the bind-mount check inspects only the top-level `Type` field. A mount with `Type: "volume"` and `VolumeOptions.DriverConfig.Options: {type: "none", o: "bind", device: "<host path>"}` is forwarded to the Docker daemon unchanged; the local volume driver then materialises it as a bind-equivalent mount, bypassing `AllowBindMountsForRegularUsers`. The same field path is accepted by the standalone `POST /volumes/create` endpoint, which never had any `AllowBindMountsForRegularUsers` check on any branch.

This undermines the administrator's configured security policy on Swarm-enabled endpoints.

## Affected Versions

The vulnerability exists in every Portainer release with Docker Swarm support — the service-creation path has never checked `CapabilityAdd`, `CapabilityDrop`, `Sysctls`, or `Privileges`, and the service-update path has never performed any `EndpointSecuritySettings` validation. The `VolumeOptions.DriverConfig` field has never been parsed by the partial service struct on any branch, so the volume-driver-bind variant (service create/update and direct `/volumes/create`) shares the same affected range.

Fixes are included in the next release of each supported branch:

| Branch              | First vulnerable | Fixed in   |
|---------------------|------------------|------------|
| 2.33.x (LTS)        | 2.33.0           | **2.33.8** |
| 2.39.x (LTS)        | 2.39.0           | **2.39.2** |
| 2.40.x (STS)        | 2.40.0           | **2.41.0** |

Portainer LTS branches receive fixes for 6 months plus a 3-month overlap after the next LTS ships. STS releases are supported only until the next STS ships — the 2.40.x STS line ends with the 2.41.0 release. All releases **prior to 2.33.0 are end-of-life** and will not receive a fix; users on EOL versions should upgrade to a supported LTS branch.

## Workarounds

Administrators who cannot immediately upgrade can reduce exposure with the following measures. None of these replaces the fix.

- **Temporarily revoke Swarm endpoint access for non-admin users** via Portainer RBAC until the patched release is deployed. This eliminates the attack surface without service disruption for administrators.
- **Segregate manager and worker nodes** with placement constraints so user workloads do not run on manager nodes. This limits the exposure of the Swarm control plane if the bypass is exploited against a worker.
- **Block creation of local-driver volumes that use `type: none` / `o: bind`** on untrusted endpoints via a daemon-side allowlist. This closes the volume-driver-bind variant until the patched release is deployed.

## Affected Code

### Service creation — only `Mounts` inspected (1/7)

```go
// api/http/proxy/factory/docker/services.go (pre-fix)

type PartialService struct {
    TaskTemplate struct {
        ContainerSpec struct {
            Mounts []struct {
                Type string
            }
        }
    }
}
```

`CapabilityAdd`, `CapabilityDrop`, `Sysctls`, and `Privileges` are not declared in the struct, so `json.Unmarshal` does not include them in the validated view. The request body is then forwarded to the Docker daemon without those fields being checked.

### Service update — no inspection (0/7)

```go
// api/http/proxy/factory/docker/transport.go (pre-fix)

if match, _ := path.Match("/services/*/*", requestPath); match {
    serviceID := path.Base(path.Dir(requestPath))
    // ... no body inspection, no call to fetchEndpointSecuritySettings ...
    return transport.restrictedResourceOperation(
        request, serviceID, serviceID,
        portainer.ServiceResourceControl, false,
    )
}
```

`fetchEndpointSecuritySettings()` is called in three places in the codebase: container creation, service creation (bind-mount check only), and volume browsing. Service update is not among them.

### Bind-mount check — driver options ignored

```go
// api/http/proxy/factory/docker/services.go (pre-fix — partial Mounts struct)

Mounts []struct {
    Type string   // only this field was read
}
```

Because `VolumeOptions.DriverConfig.Options` is not declared in the partial struct, a mount of `Type: "volume"` passes the `Type != "bind"` check and is forwarded to the daemon. The local volume driver treats `{type: "none", o: "bind", device: "<host path>"}` as a bind-equivalent mount, so the check is bypassed.

The fix extends the partial struct to carry `VolumeOptions.DriverConfig.Options map[string]string`, rejects service create/update requests where that map declares a bind-style driver, and adds a new `CheckVolumeBodyRestrictions` invocation on `POST /volumes/create` (which previously had no `AllowBindMountsForRegularUsers` check on any branch).

## Impact

An authenticated, non-admin Portainer user with access to any Docker Swarm-enabled endpoint can configure a service with:

- **Elevated Linux capabilities** including `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`, or `ALL` — not restricted by `AllowContainerCapabilitiesForRegularUsers`.
- **Disabled syscall filtering** via `Privileges.Seccomp.Mode: "unconfined"` — not restricted by `AllowSecurityOptForRegularUsers`.
- **Disabled AppArmor confinement** via `Privileges.AppArmor.Mode: "disabled"` — not restricted by `AllowSecurityOptForRegularUsers`.
- **Arbitrary sysctl values** inside the container namespace — not restricted by `AllowSysctlSettingForRegularUsers`.
- **Bind mounts of any host path**, including `/`, `/var/run/docker.sock`, SSH keys, or Portainer's own database — not restricted by `AllowBindMountsForRegularUsers`.
- **Bind-mount-equivalent host filesystem access via volume driver options** — a `Type: "volume"` mount whose `VolumeOptions.DriverConfig.Options` describe a local-driver bind, or a direct `POST /volumes/create` with the same payload, yields the same capability as a direct bind and is not restricted by `AllowBindMountsForRegularUsers`.

In combination (e.g. `CapabilityAdd:["ALL"]` + bind mount of `/`), this gives a user access equivalent to root on the Swarm manager host from a restricted account, overriding the administrator's security policy.

## Timeline

- `2026-03-12` — route2shell privately discloses the volume-driver local-bind variant.
- `2026-04-05` — JohannesLks disclosure of the Swarm service create/update bypass
- `2026-04-18`  — Fix merged to develop.
- `2026-04-29` — 2.41.0 released.
- `2026-05-07` — 2.39.2-LTS and 2.33.8-LTS released.
## Credit

- **route2shell** — disclosure of the volume-driver local-bind variant on both Swarm service creation/update and the standalone `/volumes/create` endpoint.
- **JohannesLks** — independent disclosure of the Swarm service create/update bypass

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-5fxq-qcf3-244w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44849
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
- https://github.com/portainer/portainer/releases/tag/2.41.0
