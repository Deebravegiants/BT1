# [M] OpenMcdf: Uncatchable infinite loop in DirectoryTree.TryGetDirectoryEntry on crafted CFB directory cycle

## Summary
Severity: Medium
Advisory: GHSA-5qwm-7pvp-w988
CVE: CVE-2026-45785
CWE: CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-5qwm-7pvp-w988
Type: github-advisory

## Affected
- NuGet: `OpenMcdf` — affected >=0 <3.1.4

## Details
### Summary
The BST name-lookup loop in `DirectoryTree.TryGetDirectoryEntry` (`OpenMcdf/DirectoryTree.cs:35-46`) walks directory entries by repeatedly calling `directories.TryGetSibling(child, siblingType, validateColor)`. A crafted CFB file with cyclic Left/Right sibling links among directory entries - constructed so the per-step BST-order check in `TryGetSibling` (`DirectoryEntries.cs:84-85`) is satisfied at every step - drives this `while (child is not null)` loop forever. There is no cycle detection in `TryGetDirectoryEntry`.

### Details
The recent Brent's-algorithm commit ([`24f445a`](https://github.com/openmcdf/openmcdf/commit/24f445a557fc4f46461cf6d02d296cce16c293a0)) protects `DirectoryTreeEnumerator` and works correctly for both attached repros - pure `EnumerateEntries()` throws `FileFormatException: Directory tree contains a loop` cleanly. The unprotected code path is the lookup-by-name loop, which is reached from multiple public APIs:
- `RootStorage.OpenStorage(name)` / `TryOpenStorage(name)`
- `RootStorage.OpenStream(name)` / `TryOpenStream(name)`

The second one matters most: typical consumers iterate `EnumerateEntries()` and call `OpenStream(entry.Name)` per Stream entry. With Brent's algorithm catching the enumeration cycle but not the per-entry lookup, callers can still hang as soon as they touch a streamed entry.

### PoC
Two minimal repros attached, demonstrating the same lookup-loop bug reached via two different public APIs:

- `repro_lookup.cfb` (5,632 bytes) - hangs on direct `OpenStorage(name)` for a name not present in the directory
- `repro_enumerate.cfb` (7,936 bytes) - hangs on `OpenStream(entry.Name)` called for an entry returned by `EnumerateEntries()` (the common consumer pattern)

### Repro 1 - `OpenStorage(name)`

```csharp
using OpenMcdf;

using var fs = File.OpenRead("repro_lookup.cfb");
using var root = RootStorage.Open(fs);
root.TryOpenStorage("__substg1.0_3001001F", out _);
// process spins at 100% CPU; Ctrl+C required.
```

### Repro 2 - `OpenStream` from inside an enumeration loop

```csharp
using OpenMcdf;

using var fs = File.OpenRead("repro_enumerate.cfb");
using var root = RootStorage.Open(fs);
foreach (var entry in root.EnumerateEntries())   // safe: Brent's catches enumeration cycles
{
    if (entry.Type == EntryType.Stream)
        _ = root.OpenStream(entry.Name);          // hangs: lookup path has no cycle detection
}
```

Both processes will not terminate.

(Note: pure `foreach (var entry in root.EnumerateEntries()) { }` with no per-entry lookup is **safe** - Brent's algorithm in `DirectoryTreeEnumerator` catches the enumeration cycle and throws `FileFormatException: Directory tree contains a loop`. The hang only manifests once a name lookup is performed.)

[repros.zip](https://github.com/user-attachments/files/27084338/repros.zip)

### Impact
A denial of service affecting any application that opens untrusted CFB files with OpenMcdf. A small crafted input with a cyclic directory tree reaches the unprotected BST name-lookup in `DirectoryTree.TryGetDirectoryEntry`, hit by any caller of `OpenStorage` / `TryOpenStorage` / `OpenStream` / `TryOpenStream` - including the very common pattern of iterating `EnumerateEntries()` and calling `OpenStream(entry.Name)` per Stream entry. The cycles bypass the per-step BST-order check in `TryGetSibling`, so no exception is thrown and `try/catch` cannot protect callers. The affected thread is unrecoverable without killing the process. Downstream CFB consumers (e.g. `.msg`-file parsers) inherit transitively.

## References
- https://github.com/openmcdf/openmcdf/security/advisories/GHSA-5qwm-7pvp-w988
- https://github.com/openmcdf/openmcdf
