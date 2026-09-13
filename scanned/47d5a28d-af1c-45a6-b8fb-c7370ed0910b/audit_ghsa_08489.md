# [H] Docker: Race condition in docker cp allows bind mount redirection to host path

## Summary
Severity: High
Advisory: GHSA-rg2x-37c3-w2rh
CVE: CVE-2026-42306
CWE: CWE-367, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-rg2x-37c3-w2rh
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0
- Go: `github.com/moby/moby/v2` — affected >=0 <2.0.0-beta.14
- Go: `github.com/moby/moby` — affected >=0

## Details
## Summary

A race condition during `docker cp` mount setup allows a malicious container to redirect a bind mount target to an arbitrary host path, potentially overwriting host files or causing denial of service.

## Details

When copying files into a container, the daemon sets up a temporary filesystem view by bind-mounting volumes into a private mount namespace. During this setup, the mount destination is created inside the container root and then a bind mount is attached using the container-relative path resolved to an absolute host path.

Between mountpoint creation and the `mount()` syscall, a process running inside the container can replace the destination (or a parent path component) with a symlink pointing to an arbitrary location on the host. The `mount()` syscall follows the symlink, causing the volume to be bind-mounted onto an arbitrary host path instead of the intended container path.

## Impact

A malicious container can redirect a volume bind mount to an arbitrary host path. The impact depends on the volume content and mount options:

- If the volume is writable, arbitrary host files at the redirected path could be overwritten with the volume's contents.
- If the volume is read-only, the host path is masked by the mount for the duration of the operation, causing denial of service.
- In all cases the mount is temporary (torn down after the `docker cp` completes), but the effects of any writes persist.

### Conditions for exploitation

- A container must have at least one volume mount.
- A process inside the container must be able to rapidly create and swap symlinks at the volume mount destination path.
- An operator must initiate a `docker cp` into that container, or call the `PUT /containers/{id}/archive` or `HEAD /containers/{id}/archive` API endpoints.

### Not affected

- Containers that do not have volume mounts are not affected, as the race occurs during volume bind-mount setup.

## Workarounds

- Only run containers from trusted images.
- Avoid using `docker cp` with untrusted running containers.
- Use authorization plugins to restrict access to the archive API endpoints (`PUT /containers/{id}/archive`, `HEAD /containers/{id}/archive`).

## References
- https://github.com/moby/moby/security/advisories/GHSA-rg2x-37c3-w2rh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42306
- https://github.com/moby/moby
