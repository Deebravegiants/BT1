# [M] rclone archive extract allows S3 destination prefix escape via crafted archive paths

## Summary
Severity: Medium
Advisory: GHSA-4vr5-p2gc-h23p
CVE: CVE-2026-59732
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-4vr5-p2gc-h23p
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.74.4

## Details
### Summary

`rclone archive extract` can write extracted files outside the user-selected destination prefix when extracting a crafted archive. A malicious archive entry containing parent path components such as `../` can escape the requested extraction prefix and create or overwrite sibling objects in the same bucket/path scope.

### Details

The affected code path is in `cmd/archive/extract/extract.go`.

In `ArchiveExtract()`, the archive entry path is taken from `f.NameInArchive`. The code strips only a leading `./` prefix and then joins the archive entry path with the destination directory:

```go
remote := f.NameInArchive
remote = strings.TrimPrefix(remote, "./")
if dstDir != "" {
    remote = path.Join(dstDir, remote)
}
_, err = operations.Rcat(ctx, dst, remote, fin, f.ModTime(), nil)
```

Parent path components such as `../` are not rejected before `path.Join()` is used.

When the destination is an S3-style remote such as:

```text
:s3:bucket/safe/prefix
```

rclone creates the destination filesystem rooted at `bucket/safe` and treats `prefix` as the destination directory. If the archive contains an entry named:

```text
../escaped-from-prefix.txt
```

then `path.Join("prefix", "../escaped-from-prefix.txt")` resolves to:

```text
escaped-from-prefix.txt
```

As a result, the S3 backend uploads the object to:

```text
bucket/safe/escaped-from-prefix.txt
```

instead of the expected destination:

```text
bucket/safe/prefix/escaped-from-prefix.txt
```

This allows an attacker-controlled archive to escape the selected extraction prefix on object-storage remotes.

### PoC

Test environment:

- Windows 11
- rclone v1.74.3 official Windows amd64 binary
- Local fake S3 HTTP endpoint
- Crafted ZIP archive containing `../escaped-from-prefix.txt`

Steps to reproduce:https://drive.google.com/file/d/1P_cLKFgiWSVSATB8500yP28jdzwt9FAt/view?usp=sharing

1. Extract the attached PoC ZIP.

2. Run the PoC script:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-poc.ps1 -RcloneExe "C:\path\to\rclone.exe"
```

3. The PoC creates a ZIP archive containing this entry:

```text
../escaped-from-prefix.txt
```

4. The PoC starts a local fake S3 endpoint and runs rclone with an S3-style destination prefix:

```powershell
rclone archive extract malicious.zip :s3:bucket/safe/prefix
```

5. Observe the fake S3 request log.

Expected safe behavior:

```text
PUT /bucket/safe/prefix/escaped-from-prefix.txt
```

Observed behavior:

```text
PUT /bucket/safe/escaped-from-prefix.txt?x-id=PutObject
```

This shows that the archive entry escaped the requested `safe/prefix` destination and was written under `safe/` instead.

The PoC package includes:

- `run-poc.ps1`
- `fake-s3-server.py`
- `README.md`
- `report-draft.md`
- captured proof logs

### Impact

An attacker who supplies an archive that a victim extracts with `rclone archive extract` can cause extracted files to be written outside the destination prefix selected by the victim when the destination is an S3-style object storage remote.

Depending on the victim's configured remote credentials and bucket permissions, this may allow creation or overwrite of sibling objects outside the intended extraction directory/prefix.

This does not require compromising the S3 service itself. The attack relies on the victim extracting an attacker-controlled archive with rclone into an object-storage prefix.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-4vr5-p2gc-h23p
- https://nvd.nist.gov/vuln/detail/CVE-2026-59732
- https://github.com/rclone/rclone/commit/1a746732441e8158f32fab35924b23701e719a8c
- https://github.com/rclone/rclone/commit/d11efe0d58fe6a2d6d90675bb9d8ee5840c51e1d
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.74.4
