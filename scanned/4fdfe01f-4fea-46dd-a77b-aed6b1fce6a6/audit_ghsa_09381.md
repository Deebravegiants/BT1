# [M] SharpCompress has directory traversal via directory entries in WriteToDirectory (zip slip variant)

## Summary
Severity: Medium
Advisory: GHSA-6c8g-7p36-r338
CVE: CVE-2026-44788
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-6c8g-7p36-r338
Type: github-advisory

## Affected
- NuGet: `SharpCompress` — affected >=0 <0.48.0

## Details
### Summary

A path traversal vulnerability in `IArchive.WriteToDirectory()` allows a malicious archive to create directories outside the intended extraction root. For TAR archives, this can be escalated to arbitrary file writes by chaining with a symlink entry, giving a full write primitive on the target filesystem subject to the permissions of the running process.

### Details

The vulnerable code is in the directory-entry branch of `WriteToDirectoryInternal` (sync, `IArchiveExtensions.cs:48–61`) and `WriteToDirectoryAsyncInternal` (async, `IAsyncArchiveExtensions.cs:70–84`):

```csharp
var dirPath = Path.Combine(destinationDirectory, entry.Key);
Directory.CreateDirectory(Path.GetDirectoryName(dirPath + "/"));
```

No `Path.GetFullPath()` normalisation and no bounds check are applied before the `Directory.CreateDirectory` call. Two .NET `Path.Combine` behaviours make this exploitable:

- **Relative traversal**: `Path.Combine("/safe/extract", "../../evil")` → the OS resolves `..` segments on the raw path, placing the directory outside the extraction root.
- **Absolute path override**: `Path.Combine("/safe/extract", "/tmp/evil")` → returns `"/tmp/evil"` — the base is discarded entirely for rooted paths.

File entries are **not** directly affected — they route through `ExtractionMethods.WriteEntryToDirectory` which applies the correct guard (`GetFullPath` + `StartsWith`, see `ExtractionMethods.cs:54–65`). The directory-entry branch is a separate fast-path that was added without that guard.

Affected archive formats: ZIP and TAR (non-solid). Solid archives and 7-Zip use the reader path which calls the secure method.

#### Escalation to arbitrary file writes (TAR only)

`Path.GetFullPath` on .NET does not resolve symlinks — it only normalises `.` and `..` segments. This means the file-entry guard in `ExtractionMethods.WriteEntryToDirectory` can be bypassed via symlink chaining in TAR archives when the caller supplies a `SymbolicLinkHandler`:

```csharp
archive.WriteToDirectory("/safe/extract", new ExtractionOptions
{
    ExtractFullPath = true,
    SymbolicLinkHandler = (linkPath, linkTarget) =>
        File.CreateSymbolicLink(linkPath, linkTarget)  // naive — no validation of linkTarget
});
```

Attack sequence in a single TAR archive:

1. **Symlink entry** — `link` → `../evil_outside/`
   The `SymbolicLinkHandler` creates `/safe/extract/link` pointing outside the extraction root.

2. **File entry** — `link/secret.txt`
   `ExtractionMethods.WriteEntryToDirectory` computes:
   - `destdir = Path.GetFullPath("/safe/extract/link")` → `"/safe/extract/link"` — textually inside root, check passes ✓
   - `File.Open("/safe/extract/link/secret.txt")` — OS follows symlink, file is written to `/evil_outside/secret.txt`

The library does not validate `linkTarget` before passing it to the caller's handler, and the XML docs do not warn that it may be a traversal path. The idiomatic handler implementation above is therefore silently exploitable.

ZIP does not support symlinks in SharpCompress (`ZipEntry.LinkTarget` always returns `null`), so this escalation is TAR-only.

| Attack | ZIP | TAR |
|--------|-----|-----|
| Directory traversal (escape extraction root) | Yes | Yes |
| Escalate to arbitrary file writes via symlink chain | No | Yes (if caller provides `SymbolicLinkHandler`) |

**Recommended fix** — apply the same pattern from `ExtractionMethods.WriteEntryToDirectory` to both affected files:

```csharp
var fullDestDir = Path.GetFullPath(destinationDirectory);
if (!fullDestDir.EndsWith(Path.DirectorySeparatorChar))
    fullDestDir += Path.DirectorySeparatorChar;

var dirPath = Path.GetFullPath(Path.Combine(fullDestDir, entry.Key));
if (!dirPath.StartsWith(fullDestDir, PathComparison))
    throw new ExtractionException(
        "Entry is trying to create a directory outside of the destination directory.");

Directory.CreateDirectory(dirPath);
```

Additionally, the library should validate `LinkTarget` before invoking the caller's `SymbolicLinkHandler`, or document clearly that callers must validate it themselves.

### PoC

A self-contained .NET console app is available at:
`https://github.com/svenclaesson/poc-sharpcompress-traversal`

```
git clone https://github.com/svenclaesson/poc-sharpcompress-traversal
cd poc-sharpcompress-traversal
dotnet run
```

The PoC crafts a ZIP with three directory entries (`../../escaped_relative/`, `/tmp/escaped_absolute/`, `safe_subdir/`) using `System.IO.Compression` (stdlib), then extracts with SharpCompress. Output shows `[ESCAPED]` for the two malicious entries and `[ok]` for the legitimate one, on both sync and async APIs.

Tested against SharpCompress 0.47.4 (latest NuGet).

### Impact

This is a path traversal / zip slip vulnerability (CWE-22). Any application that calls `archive.WriteToDirectory()` on an untrusted archive is affected — which covers the primary documented extraction API.

For ZIP archives the impact is limited to arbitrary directory creation, which can be used to stage privilege escalation (e.g. cron drop-ins, XDG config paths, service spool directories) or shadow expected paths to alter application behaviour.

For TAR archives, callers that implement a `SymbolicLinkHandler` — which is the only way to faithfully restore a TAR — are exposed to a full arbitrary file write primitive via the symlink chaining described above.

## References
- https://github.com/adamhathcock/sharpcompress/security/advisories/GHSA-6c8g-7p36-r338
- https://nvd.nist.gov/vuln/detail/CVE-2026-44788
- https://github.com/adamhathcock/sharpcompress/commit/2021a06626d0555a4d69471386e763ca5f5d5dfb
- https://github.com/adamhathcock/sharpcompress
