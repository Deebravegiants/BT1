# [H] Portainer has Unauthenticated Restore Endpoint that Allows Admin Takeover on Uninitialized Instances

## Summary
Severity: High
Advisory: GHSA-x626-fcwx-f5pc
CVE: CVE-2026-55761
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-x626-fcwx-f5pc
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.4
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.43.0

## Details
## Summary
Portainer supports restoring an instance from a backup archive via the /api/restore endpoint. This endpoint is intentionally unauthenticated to allow restoring before the first admin account is created, and remains accessible for the five-minute initialization window that opens each time Portainer starts. Any unauthenticated attacker with network access to a Portainer instance that has not yet been initialised can exploit this window to replace the Portainer database with a crafted archive containing attacker-controlled credentials and gain full administrative access. The same unauthenticated setup window also exposes the administrator-account-creation endpoint (`/api/users/admin/init`), which an attacker can call to create the first administrator directly; the fix gates both endpoints.

The attack requires the instance to be uninitialized, reachable by the attacker, and within the five-minute window. Once that window expires without initialization, Portainer locks its API and requires a restart to re-enable setup — each restart opens a fresh window. No credentials, session tokens, or local access are required.

## Severity
**High**

The endpoint requires no authentication and no user interaction, but successful exploitation depends on three conditions holding simultaneously: the instance must be uninitialized, reachable from the attacker's network, and within the five-minute setup window that Portainer enforces before locking the instance pending a restart. Once those conditions are met, the attack itself is straightforward — no specialized tooling or elevated privileges are needed. The vulnerable system impact is limited by the precondition: a brand new instance carries no confidential data, no existing users, and no running workloads, so the direct integrity and availability impact is low. The severity is driven entirely by the subsequent-system chain — Portainer CE is typically bound to a Docker socket that grants root-equivalent access to the host, and the compromised admin account inherits credentials and API access for every Docker host, Kubernetes cluster, and edge agent registered in the instance.

## Affected Versions

The unauthenticated initialization path has been present since the backup/restore feature was introduced.

Fixes are included in the following releases:

| Branch       | First vulnerable | Fixed in   |
|--------------|------------------|------------|
| 2.39.x (LTS) | 2.39.0           | **2.39.4** |
| 2.43.x (STS) | all prior        | **2.43.0** |

Portainer releases prior to 2.39.0 are end-of-life and will not receive a fix. This includes the 2.33.x LTS line. Users on end-of-life versions should upgrade to a supported branch.

## Workarounds
Administrators who cannot immediately upgrade can reduce exposure by:

- **Provision the administrator account at deploy time.** Start any network-reachable instance with `--admin-password` or `--admin-password-file`, supplying a pre-set administrator password. The admin account then exists from first boot, so the instance is never in the uninitialised state that the restore and admin-init endpoints depend on — there is no setup window for an attacker to race. This is the most effective workaround for new, internet- or network-facing deployments. Instances on genuinely trusted networks (air-gapped or isolated private LANs) don't require it.
- **Restrict network access to Portainer before completing initial setup.** Use firewall rules, VPC security groups, or a reverse proxy to prevent untrusted networks from reaching the Portainer API while the instance is uninitialised. Remove the restriction once an admin account has been created and initial setup is complete.
- **Complete initial setup immediately after deployment.** The initialization endpoints stop accepting requests once the instance has an administrator account. Minimising the uninitialised window limits the exploitation opportunity.
- **Audit existing deployments for unauthorised admin accounts.** If a deployment may have been accessible before setup was completed, review the admin account list and rotate all credentials.

None of these replace the fix.

## Affected Code
The vulnerability is in `api/http/handler/backup/handler.go` and `api/http/handler/backup/restore.go`. The handler registers the restore endpoint with `bouncer.PublicAccess`, bypassing all authentication middleware:

```go
// api/http/handler/backup/handler.go — NewHandler
h.Handle("/restore", bouncer.PublicAccess(httperror.LoggerHandler(h.restore))).Methods(http.MethodPost)
```

The restore handler then checks only whether the instance has been initialised before proceeding:

```go
// api/http/handler/backup/restore.go — restore
func (h *Handler) restore(w http.ResponseWriter, r *http.Request) *httperror.HandlerError {
    initialized, err := h.adminMonitor.WasInitialized()
    if err != nil {
        return httperror.InternalServerError("Failed to check system initialization", err)
    }
    if initialized {
        return httperror.BadRequest("Cannot restore already initialized instance", errors.New("system already initialized"))
    }
    h.adminMonitor.Stop()
    // Proceeds to restore the archive unconditionally
```

The fix introduces a one-time setup token that gates the public initialization endpoints — both administrator account creation (`/api/users/admin/init`) and restore (`/api/restore`) — while an instance is uninitialised. On startup, when no administrator account exists and no admin password was supplied through configuration, Portainer generates a cryptographically random token and writes it to the server logs. The restore and admin-init handlers reject any request that does not present this token in an `X-Setup-Token` header, returning `403 Forbidden`. Deployments that provision the administrator password at deploy time (`--admin-password` / `--admin-password-file`) require no token; the requirement can be pinned to an operator-chosen value (`--setup-token`) or disabled on trusted networks (`--no-setup-token`). The same change is backported to `release/2.39` for the 2.39.4 release.

## Impact
- **Full administrative access to Portainer.** The attacker replaces the database with one containing their own admin credentials and can then authenticate as a full administrator with no legitimate-user involvement.
- **Host-level compromise.** Portainer CE typically runs with access to the Docker socket (`/var/run/docker.sock`); an attacker with Portainer admin access can use container creation APIs to mount the host filesystem and execute commands as root.
- **Access to all managed environments.** The compromised Portainer admin account has credentials and API access for every Docker host, Kubernetes cluster, and edge agent registered in that instance, including any stored registry credentials, environment variables, and secrets.
- **Persistence across credential changes.** Because the attacker controls the database, they can re-insert admin credentials or maintain secondary accounts even if a legitimate user later resets the primary password via the UI.

## Timeline
- 2026-05-07: Reported privately by **um3b0shi**.
- 2026-06-04: Fix merged to `develop`.
- 2026-06-24: 2.43.0 (STS) released with the fix.
- 2026-06-25: 2.39.4 (LTS) released with the backported fix.

## Credit
- **um3b0shi** — discovered and reported the unauthenticated admin takeover via the `/api/restore` endpoint. Coverage of the companion administrator-account-creation endpoint (`/api/users/admin/init`) was added by the Portainer team as part of the fix.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-x626-fcwx-f5pc
- https://nvd.nist.gov/vuln/detail/CVE-2026-55761
- https://github.com/portainer/portainer/issues/2770
- https://github.com/portainer/portainer/commit/49f19107cf9a3540cbe406c9eb7f24390e1af02b
- https://github.com/portainer/portainer/commit/d2b56efcb4e43c4168bb6688eee9f6bf22867312
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.39.4
- https://github.com/portainer/portainer/releases/tag/2.43.0
