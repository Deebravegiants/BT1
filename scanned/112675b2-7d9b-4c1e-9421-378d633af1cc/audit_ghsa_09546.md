# [H] Portainer Has an Arbitrary File Read via Git Symlink Injection in Stack Auto-Update

## Summary
Severity: High
Advisory: GHSA-rpgq-m5fp-32wr
CVE: CVE-2026-44881
CWE: CWE-200, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rpgq-m5fp-32wr
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.2
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.41.0

## Details
## Summary
Portainer supports deploying stacks from Git repositories. When a Git-backed stack is created or updated, Portainer clones the repository using `go-git` v5, which translates Git blob entries with mode `0o120000` (symlink) into real OS symlinks on the host filesystem via `os.Symlink`. The only entry blocked from becoming a symlink is `.gitmodules`; every other path — including `docker-compose.yml`, which Portainer treats as the stack entry point — is created as a symlink without validation.

Portainer's `GET /api/stacks/{id}/file` endpoint then reads the stack entry point with `os.ReadFile`, which follows OS symlinks transparently. A repository containing `docker-compose.yml` as a symlink to an arbitrary filesystem path (for example `/etc/passwd` or a mounted Kubernetes service account token) causes the symlink target's contents to be returned verbatim in the HTTP response. Any authenticated user with rights to create or update a Git-backed stack — the default configuration in Portainer CE — can read arbitrary files accessible to the Portainer process.

The issue is amplified by Git-stack auto-update: an attacker can create a stack from a legitimate repository, pass initial review, and later push a commit that replaces `docker-compose.yml` with a symlink; the file read is then triggered on the next scheduled update cycle with no further interaction required.

## Severity
**High**

Attack complexity is Low: the attacker needs only the ability to host a Git repository and the default-granted permission to create a Git-backed stack. Privilege required is Low in typical CE deployments, where non-admin users can manage their own stacks; administrators retain the same attack surface regardless of the setting. Impact on confidentiality is High — the Portainer process commonly runs as root (required for Docker socket access), so arbitrary file read includes `/etc/shadow`, Kubernetes service account tokens, Docker secrets, environment variables, and the Portainer database itself. Integrity and availability are not directly affected, but the leaked contents (service account tokens, registry credentials, database session keys) frequently enable onward compromise of the host and managed environments.

## Affected Versions
The vulnerability exists in every Portainer release since the introduction of Git-based stack deployment support — Git-backed stacks have always performed an unrestricted `go-git` checkout and subsequently read the entry-point file through `os.ReadFile` without resolving symlinks.

Fixes are included in the following releases:

| Branch       | First vulnerable | Fixed in   |
|--------------|------------------|------------|
| 2.33.x (LTS) | 2.33.0           | **2.33.8** |
| 2.39.x (LTS) | 2.39.0           | **2.39.2** |
| 2.40.x (STS) | all prior        | **2.41.0** |

Portainer releases prior to 2.33.0 are end-of-life and will not receive a fix. Users on EOL versions should upgrade to a supported LTS branch.

## Workarounds
Administrators who cannot immediately upgrade can reduce exposure by:

- **Restricting who can create Git-backed stacks.** Disable **Allow non-admin users to manage their stacks** in environment settings so that only administrators can submit a Git repository URL. This reduces the attack to an administrator-only surface but does not remove it.
- **Avoiding untrusted repositories.** Do not deploy Git-backed stacks from repositories you do not control or review, and do not grant stack-management rights to users who can supply an arbitrary repository URL.
- **Disabling auto-update on existing stacks.** Auto-update re-clones the repository on a schedule, which allows a repository that was safe at creation time to later become malicious. Disabling auto-update removes the deferred-exploitation path.
- **Auditing existing stack working directories.** Search project paths under `/data/compose/` (or your configured data directory) for symlink entries — `find /data/compose -type l` — and treat any unexpected results as potential evidence of past exploitation.

None of these replace the fix.

## Affected Code
The vulnerability is the combination of two primitives. `go-git` translates Git symlink entries into OS symlinks unconditionally (except `.gitmodules`):

```go
// go-git v5 — Worktree.checkoutFileSymlink
func (w *Worktree) checkoutFileSymlink(f *object.File) (err error) {
    if strings.EqualFold(f.Name, gitmodulesFile) {
        return ErrGitModulesSymlink
    }
    // ... reads blob content as raw bytes ...
    err = w.Filesystem.Symlink(string(bytes), f.Name)
    return
}
```

Relative symlink targets (`../../etc/passwd`) are passed through to `os.Symlink` as-is and escape the worktree at OS resolution time. (Absolute targets are chrooted to the worktree by `go-billy`'s `ChrootHelper.Symlink` and are not useful to the attacker.)

On the read side, `GetFileContent` in `api/filesystem/filesystem.go` applies lexical path containment but not symlink resolution:

```go
func (service *Service) GetFileContent(trustedRoot, filePath string) ([]byte, error) {
    content, err := os.ReadFile(JoinPaths(trustedRoot, filePath))
    return content, err
}
```

`JoinPaths` prevents `../` traversal in the input string but does not call `filepath.EvalSymlinks`, so a symlink already written to the project path resolves through `os.ReadFile` to its ultimate target.

The fix wraps the `go-billy` filesystem used by the Git checkout with a custom `noSymlinkFS` type whose `Symlink()` method returns `ErrSymlinkDetected`, causing the clone to fail rather than write any OS symlink. Git trees that would otherwise produce a symlink entry are rejected at checkout time, closing the primary attack path. On the 2.33.x and 2.39.x branches the fix also hardens `GetFileContent` to call `filepath.EvalSymlinks` and verify the resolved path remains inside the trusted root, providing a second layer of defence against any future regression in Git-checkout handling.

## Impact
- **Arbitrary file read as the Portainer process.** Any file readable by the Portainer process — typically root in containerized deployments — can be returned through the stack file endpoint. Common targets include `/etc/shadow`, `/root/.ssh/*`, `/proc/self/environ`, and the Portainer BoltDB (`portainer.db`) which contains all user password hashes, API tokens, and agent credentials.
- **Kubernetes service account token exposure.** Portainer running on Kubernetes has its cluster service account token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`; reading it grants the attacker the Portainer pod's cluster API access.
- **Docker Swarm secret exposure.** Secrets mounted into the Portainer container at `/run/secrets/` (for example the initial admin password in Swarm deployments) are readable with the same mechanism.
- **Onward compromise.** Leaked service tokens, registry credentials, and database contents frequently enable authenticated access to managed Docker/Kubernetes environments, container registries, and Portainer itself under other users' identities.
- **Deferred exploitation via auto-update.** A repository that passes initial review at stack creation can be mutated afterwards; the malicious commit takes effect on the next auto-update cycle without user interaction.

## Timeline
- 2026-03-20: Reported via GitHub Security Advisory by **b-hermes**.
- 2026-04-18: Fix merged to `develop`.
- 2026-04-29: 2.41.0 released with fix.
- 2026-05-07: 2.33.8, 2.39.2, released with fix.

## Credit
- **b-hermes** — identified the Git symlink injection primitive, traced the end-to-end chain through `GetFileContent`, and provided a fully validated proof-of-concept.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-rpgq-m5fp-32wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44881
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
- https://github.com/portainer/portainer/releases/tag/2.41.0
