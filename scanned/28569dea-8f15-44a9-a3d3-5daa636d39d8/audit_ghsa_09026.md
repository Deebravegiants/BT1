# [M] Sparkle: Binary delta apply intermediate-symlink traversal in malicious .delta

## Summary
Severity: Medium
Advisory: GHSA-hg88-v3cw-3qrh
CVE: CVE-2026-47121
CWE: CWE-22, CWE-59
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-hg88-v3cw-3qrh
Type: github-advisory

## Affected
- SwiftURL: `github.com/sparkle-project/Sparkle` — affected >=0 <2.9.2

## Details
## Summary

Binary delta apply intermediate-symlink traversal in malicious .delta

`Autoupdate/SUBinaryDeltaApply.m` enforces `relativePath.pathComponents containsObject:@".."` and rejects writes whose immediate parent directory IS itself a symbolic link, but does not detect symlinks deeper in the relative path. `Autoupdate/SPUSparkleDeltaArchive.m`'s `extractItem:` will create symlinks in the destination tree from archive content (no `..` check on the symlink target), and a subsequent `Extract` item targeting `<symlink>/foo/bar` then escapes the destination tree via `fopen(path, "wb")` because the kernel resolves the intermediate symlink during the open call.

This is a defense-in-depth issue: exploitation requires a maliciously-crafted `.delta` that passes EdDSA signature verification, i.e. EdDSA private-key compromise. With the AppInstaller running as root for system-domain installs, it gives the holder of a stolen signing key arbitrary file write at root level via the delta-apply path, which is a strictly broader primitive than the "drop-in replacement bundle" install they would otherwise have.

Affected versions: 1.x (master branch), 2.x branch including 2.9.1.

## Details

### Symlink writeable from archive

`Autoupdate/SPUSparkleDeltaArchive.m:557-678`'s `extractItem:` handles symlinks if the archive item carries `S_ISLNK(mode)`:

```objc
} else {
    // Link files

    if (PARTIAL_IO_CHUNK_SIZE < decodedLength) { ...too long... }
    if (decodedLength > PATH_MAX) { ...too long... }

    char buffer[PATH_MAX + 1] = {0};
    if (![self _readBuffer:buffer length:(int32_t)decodedLength]) { ... }

    NSString *destinationPath = [fileManager stringWithFileSystemRepresentation:buffer length:decodedLength];

    [fileManager removeItemAtPath:itemFilePath error:NULL];

    NSError *createLinkError = nil;
    if (![fileManager createSymbolicLinkAtPath:itemFilePath withDestinationPath:destinationPath error:&createLinkError]) {
        _error = createLinkError;
        return NO;
    }
    ...
    lchmod(itemFilePathString, mode);
}
```

The link's `destinationPath` is taken verbatim from the archive content with only a length cap; absolute paths and `..` are accepted. After this item is processed, the destination tree contains a symlink that points outside it.

### Parent-symlink check is shallow

`Autoupdate/SUBinaryDeltaApply.m:177-207`:

```objc
[archive enumerateItems:^(SPUDeltaArchiveItem *item, BOOL *stop) {
    NSString *relativePath = item.relativeFilePath;

    if ([relativePath.pathComponents containsObject:@".."]) {
        ...reject...
    }

    NSString *sourceFilePath = [source stringByAppendingPathComponent:relativePath];
    NSString *destinationFilePath = [destination stringByAppendingPathComponent:relativePath];
    {
        NSString *destinationParentDirectory = destinationFilePath.stringByDeletingLastPathComponent;
        NSDictionary<NSFileAttributeKey, id> *destinationParentDirectoryAttributes = [fileManager attributesOfItemAtPath:destinationParentDirectory error:NULL];

        // It is OK for the directory parent to not exist if it has already been removed
        if (destinationParentDirectoryAttributes != nil) {
            NSString *fileType = destinationParentDirectoryAttributes[NSFileType];
            if ([fileType isEqualToString:NSFileTypeSymbolicLink]) {
                ...reject...
            }
        }
    }
    ...
}];
```

Two gaps:

1. The check inspects only `destinationParentDirectory` (one level up), not all intermediate components. For a relative path `a/b/c.txt`, the kernel resolves through any symlink at component `a`. `attributesOfItemAtPath:` with the resolved path returns attributes of the resolved-through directory, which is `NSFileTypeDirectory` (not `NSFileTypeSymbolicLink`), so the check passes.

2. The check is skipped entirely if `destinationParentDirectoryAttributes == nil` (line 195). When the symlink target is to a directory that does not contain the named subpath, the parent appears not to exist and the check is skipped. The subsequent `fopen(path, "wb")` then creates the file along the resolved path.

### Write primitive

For an item with `SPUDeltaItemCommandExtract` set, `SUBinaryDeltaApply.m:354-365` calls `[archive extractItem:item]` which goes through `SPUSparkleDeltaArchive.m:574-622` for regular files:

```objc
[fileManager removeItemAtPath:itemFilePath error:NULL];

char itemFilePathString[PATH_MAX + 1] = {0};
if (![itemFilePath getFileSystemRepresentation:itemFilePathString maxLength:sizeof(itemFilePathString) - 1]) { ... }

FILE *outputFile = fopen(itemFilePathString, "wb");
```

`fopen(path, "wb")` follows symlinks at every path component and creates/truncates the file at the resolved path. If `<dest>/a` is a symlink to `/Library/LaunchDaemons` (for a root install) and the relative path is `a/com.attacker.plist`, the call writes `/Library/LaunchDaemons/com.attacker.plist`.

The `chmod` follow-up at `SUBinaryDeltaApply.m:335` (`chmod(destinationFilePath.fileSystemRepresentation, sourceFileInfo.st_mode)`) and `SPUSparkleDeltaArchive.m:619` (`chmod(itemFilePathString, mode)`) likewise follows symlinks, so attacker-chosen permissions land on the attacker-chosen target.

### Threat model

This primitive is reachable only when the archive can pass EdDSA signature verification, which requires either:

- The developer's private signing key has been compromised, or
- A separate vulnerability allows bypassing `SUSignatureVerifier` (none was identified in this review).

Given a stolen private key, the attacker already has the ability to push a normal full-bundle update. The delta-apply traversal grants strictly more: arbitrary file write into directories outside `<destination>`. When the AppInstaller runs in the system domain (root), this becomes arbitrary file write as root, which is qualitatively broader than "replace the app bundle".

It is therefore worth fixing as a defense-in-depth measure, even though the prerequisite (key compromise) is itself a worst case.

## PoC

The PoC requires a valid EdDSA signature on the malicious `.delta` archive. With a test signing key under your control (any Sparkle test fixture key), generate a delta as follows:

1. Construct the archive payload with two items, in this order, using the `SPUSparkleDeltaArchive` writer (or by hand-assembling the format described in `SPUSparkleDeltaArchive.m` and `SPUDeltaArchiveProtocol.h`):

```
Item 1:
  relativeFilePath = "Contents/Resources/escape"
  commands         = SPUDeltaItemCommandExtract  (= 0x02)
  mode             = S_IFLNK | 0o755             (= 0xA1ED)
  payload          = "/Library/LaunchDaemons"

Item 2:
  relativeFilePath = "Contents/Resources/escape/com.attacker.persistence.plist"
  commands         = SPUDeltaItemCommandExtract  (= 0x02)
  mode             = S_IFREG | 0o644             (= 0x81A4)
  payload          = <attacker-chosen LaunchDaemon plist bytes>
```

2. Sign the archive with the test EdDSA key, publish it as a delta enclosure with matching `sparkle:edSignature`, and host it from a feed pointed at by a Sparkle host whose old-bundle public key matches.

3. Trigger a system-domain install. The flow:
   - `applyBinaryDelta` enumerates items.
   - Item 1 passes the `..` check (the path components are `Contents`, `Resources`, `escape` - no `..`). The parent `Contents/Resources` exists in the source-copy and is a directory, not a symlink. The check passes. `extractItem:` for `S_ISLNK(mode)` calls `createSymbolicLinkAtPath:withDestinationPath:` and creates `<dest>/Contents/Resources/escape -> /Library/LaunchDaemons`.
   - Item 2 passes the `..` check. Its parent `<dest>/Contents/Resources/escape` resolves through the just-created symlink to `/Library/LaunchDaemons`, whose attributes are returned as `NSFileTypeDirectory` (not symlink). The check passes.
   - `extractItem:` for `S_ISREG(mode)` does `removeItemAtPath` (no-op, target file does not yet exist) then `fopen("<dest>/Contents/Resources/escape/com.attacker.persistence.plist", "wb")`. The kernel resolves the symlink and creates `/Library/LaunchDaemons/com.attacker.persistence.plist`.
   - The hash check at the end of `applyBinaryDelta` (`getRawHashOfTreeWithVersion(afterHash, finalDestination, ...)`) is computed only against `finalDestination`. The file dropped at `/Library/LaunchDaemons/` is outside that tree and does not affect the hash. The hash check still passes (or, if it does not because the dest tree is missing the file, the dropped LaunchDaemon plist is still left behind - destination cleanup at line 471 only removes `finalDestination`, not the escape target).

4. Observed result: a root-owned LaunchDaemon plist exists at `/Library/LaunchDaemons/com.attacker.persistence.plist`. On next reboot it is launched as root.

A simpler proof-of-concept that does not require a system-domain install: target a user-writable directory (e.g. `~/Library/LaunchAgents/`), use a user-domain Sparkle host. The same item-pair lands a user-level LaunchAgent at next login.

## Impact

Defense-in-depth gap: the holder of a compromised EdDSA signing key gains a primitive (arbitrary file write at the privilege of the AppInstaller process) that exceeds what an "install a malicious bundle" path provides. For system-domain installs this is arbitrary file write as root, including locations outside the target app bundle (`/Library/LaunchDaemons`, `/etc/...` subpaths that exist as directories, `/usr/local/`, etc.).

Recommended fix: in `SUBinaryDeltaApply.m`, walk every component of `relativePath` and reject if any intermediate component is a symlink (or refuse to allow the archive to create symlinks during apply at all, given the limited number of legitimate use cases for symlinks inside an `.app` bundle and the existing `lchmod` already in place). Cleanup on failure should also `removeTree` along the symlink target, not just `finalDestination`.

## References
- https://github.com/sparkle-project/Sparkle/security/advisories/GHSA-hg88-v3cw-3qrh
- https://github.com/sparkle-project/Sparkle/commit/fe7b718d0736f3e139e374e26fbca96f29e13bf0
- https://github.com/sparkle-project/Sparkle
