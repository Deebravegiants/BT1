# [M] Aqua's archive extraction follows attacker-planted symlinks, allowing writes outside the install directory

## Summary
Severity: Medium
Advisory: GHSA-mf5c-hw34-4hpp
CVE: CVE-2026-55569
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-mf5c-hw34-4hpp
Type: github-advisory

## Affected
- Go: `github.com/aquaproj/aqua/v2` — affected >=0 <2.60.1

## Details
### Summary

`aquaproj/aqua` extracts downloaded tool archives through `pkg/unarchive/archives.go` using `github.com/mholt/archives`. The archive handler creates symlink entries with `os.Symlink(f.LinkTarget, dstPath)` without validating that the symlink target resolves inside the extraction destination. A subsequent regular-file archive entry with the same path is opened with `OpenFile(dstPath, O_CREATE|O_WRONLY)`, which follows the attacker-planted symlink.

A malicious or compromised aqua package / release asset can therefore write attacker-controlled bytes outside aqua's extraction directory, with the privileges of the user running aqua.

### Details

Affected file: `pkg/unarchive/archives.go`

Affected function: `(*handler).HandleFile`

The vulnerable logic is the combination of:

```go
os.Symlink(f.LinkTarget, dstPath)
```

for symlink entries, followed by:

```go
h.fs.OpenFile(dstPath, os.O_CREATE|os.O_WRONLY, f.Mode())
```

for a later regular file entry at the same archive path. The symlink target is not jailed to the extraction destination, and the later file open follows the symlink.

The attached PoC uses a two-entry `tar.gz` archive:

1. symlink `pwn -> <outside target>`;
2. regular file `pwn` containing attacker-controlled bytes.

The same `mholt/archives` extraction flow is used for the vulnerable handler and for a negative-control handler using a destination-root jail.

### PoC

Attachment: `submission_aqua_archive_symlink_traversal_v2_final.zip`

Run:

```bash
go run mkarchive.go /tmp/aqua-outside-target
go build -o aqua-archive-poc .
mkdir -p /tmp/aqua-dest
./aqua-archive-poc vuln /tmp/aqua-dest malicious.tar.gz
cat /tmp/aqua-outside-target

mkdir -p /tmp/aqua-dest-safe
./aqua-archive-poc safe /tmp/aqua-dest-safe malicious.tar.gz
```

Expected vulnerable result:

```text
/tmp/aqua-outside-target contains PWNED_BY_AQUA_SYMLINK_TRAVERSAL
```

Expected safe-control result:

```text
The escaping symlink / write is rejected and the outside target is unchanged.
```

### Impact

An attacker who controls an archive that aqua installs can write attacker-controlled content to paths outside the extraction destination, limited by the filesystem permissions of the user running aqua. This can lead to user-level code execution if the overwritten path is later executed or interpreted, for example a shell startup file, a tool configuration file, or a writable PATH entry.

This report does not claim privilege escalation beyond the aqua process privileges.

## References
- https://github.com/aquaproj/aqua/security/advisories/GHSA-mf5c-hw34-4hpp
- https://github.com/aquaproj/aqua/commit/d5b02b220188de376a661b3aabfa912202a1a59a
- https://github.com/aquaproj/aqua
- https://github.com/aquaproj/aqua/releases/tag/v2.60.1
