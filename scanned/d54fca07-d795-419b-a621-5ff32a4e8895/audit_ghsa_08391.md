# [M] Portainer has a path traversal in backup archive extraction that allows arbitrary file write

## Summary
Severity: Medium
Advisory: GHSA-m8fg-67j7-cx4v
CVE: CVE-2026-44885
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-m8fg-67j7-cx4v
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8

## Details
### Summary
Portainer's backup restore feature accepts a `.tar.gz` archive and extracts it to a target directory on the server. The extraction function (`ExtractTarGz` in `api/archive/targz.go`) constructed output paths using `filepath.Clean(filepath.Join(outputDirPath, header.Name))`. This combination does not prevent directory traversal — a tar entry named `../../etc/cron.d/evil` resolves to a path outside the extraction root, so a crafted archive can write files to arbitrary locations on the server filesystem.

## Severity

**Medium**

**CWE-22** — Improper Limitation of a Pathname to a Restricted Directory
('Path Traversal')

Exploitation requires administrator access to Portainer's backup restore endpoint. An administrator who is deceived into restoring a malicious archive, or whose credentials are compromised, can use this path to write files outside the Portainer data directory.

## Affected Versions

The vulnerability exists in every Portainer release prior to 2.39.0 — `ExtractTarGz` has used `filepath.Clean(filepath.Join())` since it was introduced.  The fix shipped with 2.39.0 (patched on `develop` before the 2.39 branch cut); 2.34.x–2.38.x STS releases are also affected but are end-of-life and will not receive a fix.

| Branch       | First vulnerable | Fixed in   |
|--------------|------------------|------------|
| 2.33.x (LTS) | 2.33.0           | **2.33.8** |

Portainer 2.39.0 and later are not affected — the fix was present from the initial 2.39.0 release. All releases prior to 2.33.0 are end-of-life and will not receive a fix; users on EOL versions should upgrade to a supported release.

## Workarounds

Administrators who cannot immediately upgrade should:

- **Only restore archives from trusted sources.** Do not restore archives received from untrusted parties or transmitted over unencrypted channels.
- **Use backup encryption.** Portainer's optional backup encryption requires the correct passphrase to decrypt before extraction; an attacker without the passphrase cannot craft a valid encrypted archive.

Neither of these replaces the fix.

## Affected Code

`ExtractTarGz` in `api/archive/targz.go` constructed output paths without safe containment:

```go
// api/archive/targz.go (pre-fix)
case tar.TypeReg:
    p := filepath.Clean(filepath.Join(outputDirPath, header.Name))
```
filepath.Join resolves ../ components lexically and filepath.Clean normalises the result, but neither verifies the final path remains inside outputDirPath. The fix replaces this with filesystem.JoinPaths, which forces all path components to be relative to the trusted root:

```go
// api/archive/targz.go (post-fix)
case tar.TypeReg:
    p := filesystem.JoinPaths(outputDirPath, header.Name)
```

### Impact

- Arbitrary file write at any path accessible to the Portainer process (typically root in containerised deployments), overriding filesystem boundaries of the data directory.
- Potential host persistence by writing to cron directories, SSH authorised key files, or executable paths, depending on how the container is configured and what host paths are accessible.

The practical severity is reduced because exploitation requires administrative privileges within Portainer.

## Timeline

- 2026-02-16: Fix merged to develop ([#1875](https://github.com/portainer/portainer-suite/pull/1875)).
- 2026-02-25: 2.39.0 released with fix.
- 2026-05-07: 2.33.8 released with backport fix.

### Credits
Reported by [Kolega](https://kolega.ai).

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-m8fg-67j7-cx4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44885
- https://github.com/portainer/portainer-suite/pull/1875
- https://github.com/portainer/portainer/commit/e02ae6b2fb69668d1cd7d07cb873dfcdd9cf1e42
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
