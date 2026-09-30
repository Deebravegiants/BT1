# [M] Docker: Race condition in docker cp allows creation of arbitrary empty files on the host via symlink swap

## Summary
Severity: Medium
Advisory: GHSA-vp62-88p7-qqf5
CVE: CVE-2026-41568
CWE: CWE-367, CWE-61, CWE-81
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-vp62-88p7-qqf5
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0
- Go: `github.com/moby/moby/v2` — affected >=0 <2.0.0-beta.14
- Go: `github.com/moby/moby` — affected >=0

## Details
## Summary

A race condition during `docker cp` mount setup allows a malicious container to create empty files or directories at arbitrary absolute paths on the host filesystem.

This advisory covers the race during mountpoint creation. The related race during the subsequent mount syscall is tracked in GHSA-rg2x-37c3-w2rh

## Details

When copying files into a container, the daemon sets up a temporary filesystem view by bind-mounting volumes into a private mount namespace. During this setup, the mount destination path is first resolved within the container's root filesystem using `GetResourcePath`, and then used to create the mountpoint (file or directory) if it does not already exist via `createIfNotExists`.

Between path resolution and mountpoint creation, a process running inside the container can swap a path component for a symlink pointing to an arbitrary location on the host. Because `createIfNotExists` operates on the already-resolved absolute path using standard `os.MkdirAll` and `os.OpenFile` — which follow symlinks in intermediate path components — the symlink is followed and the file or directory is created outside the container root filesystem, as root.

## Impact

A malicious container can create empty files or directories at arbitrary absolute paths on the host filesystem, running as root. This enables persistent denial of service — for example:

- Converting `/etc/docker/daemon.json` into a directory prevents the daemon from restarting
- Creating `/etc/nologin` prevents user logins
- Overwriting critical system paths with empty files can break host services

The container does not gain read or write access to existing host files — only the ability to create new empty files or directories at chosen paths.

### Conditions for exploitation

- A container must be running with a process that can rapidly create and swap symlinks at a volume mount destination path.
- An operator must initiate a `docker cp` into that container, or call the `PUT /containers/{id}/archive` or `HEAD /containers/{id}/archive` API endpoints.

### Not affected

- Containers that do not have volume mounts are not affected, as the race occurs during volume bind-mount setup.

## Patches

Mountpoint creation is now scoped to the container root using `os.Root` (Go 1.24+), which refuses to follow symlinks that escape the opened root directory. All filesystem operations in `createIfNotExists` (`MkdirAll`, `OpenFile`) are performed through the `os.Root` handle, so even if a symlink swap occurs after path resolution, the creation stays confined to the container root.

## Workarounds

- Only run containers from trusted images.
- Avoid using `docker cp` with untrusted running containers.
- Use authorization plugins to restrict access to the archive API endpoints (`PUT /containers/{id}/archive`, `HEAD /containers/{id}/archive`).

## References
- https://github.com/moby/moby/security/advisories/GHSA-vp62-88p7-qqf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41568
- https://github.com/moby/moby
