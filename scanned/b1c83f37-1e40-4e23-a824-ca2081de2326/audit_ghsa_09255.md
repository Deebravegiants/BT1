# [H] Portainer has a bind-mount restriction bypass via HostConfig.Mounts

## Summary
Severity: High
Advisory: GHSA-7fw3-x4r2-g7wc
CVE: CVE-2026-44850
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-7fw3-x4r2-g7wc
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.2
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.41.0

## Details
## Summary

Portainer offers an environment-level **Disable bind mounts for non-administrators** security setting that blocks regular users from binding host paths into containers they create through the Portainer-mediated Docker API. The check that enforces this setting only inspected the legacy `HostConfig.Binds` array on the container-create proxy and never looked at the equivalent `HostConfig.Mounts` array. Any authenticated user with rights to create containers on a Docker environment where the restriction is enabled could submit a `bind`-typed entry under `HostConfig.Mounts` and mount any host path into their container.

The two fields are interchangeable on the Docker daemon — both produce real bind mounts at runtime — so a check that inspects only one is functionally equivalent to no check at all. The same primitive is correctly enforced on Swarm service create against `TaskTemplate.ContainerSpec.Mounts`; the gap was specific to the `POST /containers/create` proxy path.

Exploitation requires a regular user with container-create rights on an environment that has the restriction enabled. Such a user can mount any host path read-write or read-only into a container they own and use the resulting view of the host filesystem to read or write anything the Docker daemon's user can — typically `root`. Bind-mount restriction is the primary defence against host filesystem exposure on shared environments where regular users are otherwise permitted to deploy containers.

## Severity

**High**

The vulnerability is exploitable over the network with low attack complexity, no attack requirement, and no user interaction. It requires a low-privilege authenticated session — any regular user with container-create rights on an environment where the bind-mount restriction is enabled. The vulnerable system (the Portainer container-create proxy) suffers a confidentiality and integrity breach by virtue of the bypass itself, but the dominant impact is on the subsequent system: the Docker host's filesystem and any container running alongside the attacker's. This is a restriction bypass rather than a cross-authority escalation — the user already had container-create rights, and the bind-mount restriction is a defence-in-depth control on top of that capability — which is the reason the rating is held at High rather than promoted to Critical despite the host-level reach.

## Affected Versions

The vulnerability has existed since the `AllowBindMountsForRegularUsers` security setting was introduced. The `HostConfig.Mounts` field has never been inspected by the container-create proxy on any release line.

Fixes are included in the following releases:

| Branch       | First vulnerable | Fixed in   |
|--------------|------------------|------------|
| 2.33.x (LTS) | 2.33.0           | **2.33.8** |
| 2.39.x (LTS) | 2.39.0           | **2.39.2** |
| 2.41.x (STS) | all prior        | **2.41.0** |

Portainer releases prior to 2.33.0 are end-of-life and will not receive a fix. Users on EOL versions should upgrade to a supported LTS branch.

## Workarounds

Administrators who cannot immediately upgrade can reduce exposure by:

- **Revoke container-create rights from non-administrator accounts on affected environments.** If the bind-mount restriction is being relied on as a hard guarantee, audit which non-administrator accounts have container-create rights on environments where it is set, and downgrade those accounts to roles that lack container-create until the patched release is deployed. Stack and service deployment that depends on container-create will stop working for those users until the patched release is in place.
- **Audit recent container creations for `HostConfig.Mounts` of `Type: bind` from non-admin Portainer users.** Inspect Docker daemon logs and `docker inspect` output on affected environments. Any non-admin-created container with a bind-typed `Mounts` entry should be treated as a potential incident.
- **Segregate tenants by environment.** Where the per-environment toggle was being used to share an environment between tenants of different trust levels, splitting the workloads onto separate environments is a stronger control than the toggle and remains in place after upgrade.

None of these replace the fix.

## Affected Code

The enforcement lives in `decorateContainerCreationOperation` in `package/server-ce/api/http/proxy/factory/docker/containers.go`. The `PartialContainer` struct used to deserialise the request body for inspection only contained `HostConfig.Binds`:

```
// package/server-ce/api/http/proxy/factory/docker/containers.go
type PartialContainer struct {
    HostConfig struct {
        Privileged bool           `json:"Privileged"`
        PidMode    string         `json:"PidMode"`
        Devices    []any          `json:"Devices"`
        Sysctls    map[string]any `json:"Sysctls"`
        CapAdd     []string       `json:"CapAdd"`
        CapDrop    []string       `json:"CapDrop"`
        Binds      []string       `json:"Binds"`
    } `json:"HostConfig"`
}

if !securitySettings.AllowBindMountsForRegularUsers && len(partialContainer.HostConfig.Binds) > 0 {
    for _, bind := range partialContainer.HostConfig.Binds {
        if strings.HasPrefix(bind, "/") {
            return forbiddenResponse, ErrBindMountsForbidden
        }
    }
}
```

The fix adds a `Mounts` field to `PartialContainer` and a parallel check that rejects any entry whose `Type` equals `bind`, mirroring the existing logic on the Swarm service-create proxy. The container-update path is unaffected — the Docker daemon does not accept mount changes via container update — and Swarm service create was already covered. Compose-stack deployment is not in scope of this advisory; the bind-mount restriction is a daemon-mediated container-create control, and Compose deployment runs Docker through a separate path that is not currently subject to the same restriction.

The same change applies cleanly on each LTS branch — the surrounding code shape on `release/2.33` and `release/2.39` is identical to develop on the points the patch touches, so the LTS backports are byte-equivalent additions of the `Mounts` field and the parallel check.

## Impact

A regular user who has been explicitly restricted from using bind mounts can bypass the restriction and:

- **Read or write any path on the Docker host filesystem.** The mount runs as the daemon user (typically `root`), so any path is reachable. Sensitive examples include `/etc/shadow`, host SSH keys under `/root/.ssh` and `/home/*/.ssh`, and TLS material under `/etc/docker`.
- **Compromise other containers on the same host.** The host's `/var/lib/docker` (or equivalent) is reachable from within the bound mount, exposing the layers, volumes, and live state of every container the daemon manages.
- **Reach the Docker socket.** Mounting `/var/run/docker.sock` into the attacker's container hands them full Docker API access on the host, regardless of any authorisation enforced by Portainer above the proxy.
- **Write persistence to the host.** Without `ReadOnly`, the attacker can drop SSH keys into `authorized_keys`, install systemd units, or modify cron, achieving persistence outside of any container the daemon supervises.

The bind-mount restriction was the primary defence against this class of host exposure for non-administrator container creators; bypassing it removes the only enforcement point above the daemon for tenants who were granted container-create rights.

## Timeline

- 2026-03-04: Reported via GitHub Security Advisory by **offensiveee** (Assaf Alassaf).
- 2026-03-04 – 2026-04-17: Six further independent reports of the same primitive received via GitHub Security Advisory (alexwaira, ffulbtech, Proscan-one, jeroengui, AyushParkara, marduc812) and consolidated against this advisory.
- 2026-04-18: Fix merged to `develop`.
- 2026-06-04: Backports merged to `release/2.33` and `release/2.39`.
- 2026-04-29: 2.41.0 released with fix.
- 2026-05-07: 2.33.8, 2.39.2, released with fix.

## Credit

- **offensiveee** (Assaf Alassaf) — initial report identifying the `HostConfig.Mounts` bypass on container create and the divergence from the Swarm service-create check.
- **alexwaira** — independently reported the same `HostConfig.Mounts` bypass on container create.
- **ffulbtech** — independently reported the same `HostConfig.Mounts` bypass on container create.
- **Proscan-one** — independently reported the same `HostConfig.Mounts` bypass on container create.
- **jeroengui** — independently reported the same `HostConfig.Mounts` bypass on container create.
- **AyushParkara** — independently reported the same `HostConfig.Mounts` bypass on container create.
- **marduc812** — independently reported the same `HostConfig.Mounts` bypass on container create.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-7fw3-x4r2-g7wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44850
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
- https://github.com/portainer/portainer/releases/tag/2.41.0
