# [M] node-tar: Process crash via PAX numeric path type confusion

## Summary
Severity: Medium
Advisory: GHSA-w8wr-v893-vjvp
CVE: CVE-2026-59871
CWE: CWE-704
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-w8wr-v893-vjvp
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.18

## Details
### Summary

A crafted 2.5KB tar archive crashes any Node.js process that extracts it. The PAX header parser coerces all-digit path values to JavaScript numbers, which causes an uncaught TypeError when downstream code calls `.split('/')` on the numeric value. Error handlers and `strict: false` cannot intercept the crash.

### Details

In `pax.ts` line 180, `parseKV` converts PAX values matching `/^[0-9]+$/` to numbers via `+v`. This applies to all fields including `path` and `linkpath`. When a PAX header sets `path` to an all-digit string like `"12345"`, the value becomes the number `12345`.

This number flows through Header -> ReadEntry -> Unpack.CHECKPATH, where `normalizeWindowsPath(entry.path).split('/')` throws a TypeError because numbers don't have `.split()`.

The throw is synchronous during event emission and bypasses all error handling:
- `strict: false` does not help
- `'error'` event handlers do not catch it
- `'warn'` handlers do not catch it
- The TypeError propagates through the event emitter stack as an uncaughtException

Directory, SymbolicLink, and Link type entries reach CHECKPATH and crash. File type entries crash earlier in Header constructor at `this.path.slice(-1)`, but that throw is caught and emitted as a warning only.

### PoC

Create a tar archive with a PAX extended header containing an all-digit path:

```
PAX header body: "18 path=12345\n"
Entry type: Directory (type '5')
```

Extract it:
```js
const tar = require('tar');

// All of these crash with TypeError: t.split is not a function
tar.extract({ file: 'malicious.tar', cwd: '/tmp/test' });

// Error handlers don't help:
tar.extract({ file: 'malicious.tar', cwd: '/tmp/test', strict: false })
  .on('error', (err) => { /* never reached */ })
  .on('warn', (code, msg) => { /* never reached */ });
```

The archive is ~2.5KB. The crash is deterministic on every attempt.

### Impact

Denial of service. Any application or tool that extracts untrusted tar archives crashes from a single small file. This includes npm (which uses node-tar to extract packages), CI/CD pipelines, file upload processors, and backup tools. The crash cannot be caught by application-level error handling.

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-w8wr-v893-vjvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-59871
- https://github.com/isaacs/node-tar/commit/e02a4e9e013c4be95302e2eb2047a942b883c27b
- https://github.com/isaacs/node-tar
- https://github.com/isaacs/node-tar/releases/tag/v7.5.18
