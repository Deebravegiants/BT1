# [M] Pterodactyl Wings: Chmod operation can be used to change permissions of files outside of the server container

## Summary
Severity: Medium
Advisory: GHSA-rhq6-9rgh-v45c
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-rhq6-9rgh-v45c
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=1.11.9 <1.12.2

## Details
In `wings/internal/ufs/fs_unix.go` (line 92-94), this function is defined and is used to change permissions of files in the server:

```go
func (fs *UnixFS) fchmodat(op string, dirfd int, name string, mode FileMode) error {
   return ensurePathError(unix.Fchmodat(dirfd, name, uint32(mode), 0), op, name)
}
```

This call to the unix function `fchmodat(int fd, char* name, mode_t mode, int flags)`  does not have the flag `AT_SYMLINK_NOFOLLOW` set, and Wings neither checks or validate if the target file is a symlink. This allows one to change permissions of files or folders outside of the server container by making symlinks to existing files in the host and then chmoding it.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-rhq6-9rgh-v45c
- https://github.com/pterodactyl/wings
