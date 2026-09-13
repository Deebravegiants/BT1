# [M] ep_etherpad-lite: Import/export uses Math.random() for temp file paths; predictable paths on shared /tmp enable symlink-based file overwrite

## Summary
Severity: Medium
Advisory: GHSA-2jwf-f4xq-f24h
CVE: CVE-2026-55086
CWE: CWE-377, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-2jwf-f4xq-f24h
Type: github-advisory

## Affected
- npm: `ep_etherpad-lite` — affected >=0 <3.1.0

## Details
## Description

`src/node/handler/ImportHandler.ts` and `src/node/handler/ExportHandler.ts` both compute their temporary working-file paths as:

```ts
const randNum = Math.floor(Math.random() * 0xFFFFFFFF);
const srcFile = `${os.tmpdir()}/etherpad_export_${randNum}.html`;
const destFile = `${os.tmpdir()}/etherpad_export_${randNum}.${type}`;
```

Two flaws compound:

1. **`Math.random()` is not crypto-secure.** It yields at most ~32 bits of entropy and is **predictable across calls within the same Node process** (V8 shares PRNG state between consecutive `Math.random()` invocations). An attacker on the same host who observes any earlier temp-file name from logs or other side channels can predict subsequent names.

2. **The paths land in `os.tmpdir()`.** On a typical Linux system this is `/tmp` — a shared world-writable directory. An unprivileged local attacker can pre-create a symbolic link at a predicted path pointing at any file the Etherpad process can write:

   ```
   ln -s /etc/etherpad/SESSIONKEY.txt /tmp/etherpad_export_<predicted>.html
   ```

   When `ExportHandler` calls `fs.writeFile(srcFile, html)` (or `ImportHandler` calls `fs.rename(srcFile, destFile)` / `soffice` writes its converted output to the path), the open syscall follows the symlink and either reads from or overwrites the linked target. For deployments where the Etherpad process runs as a privileged user (notably some Docker base images that run as root, snap confinement edge cases, or hand-rolled systemd units), this becomes arbitrary file overwrite.

The Import path is more impactful in practice: the file content the attacker can land in the symlink target is partially attacker-controlled (the post-soffice/post-mammoth conversion output of the uploaded document).

## Severity rationale

- **AV:L** — requires local access to the host that runs Etherpad. Multi-tenant hosts (shared dev boxes, k8s shared-node setups, single-server CI workers) are the realistic threat surface.
- **AC:H** — attacker needs to predict the temp filename, which requires observing prior names or shared PRNG state.
- **PR:L** — any unprivileged local account.
- **UI:N** — no user interaction.
- **S:C** — scope change from local user to whatever the Etherpad process can write.
- **C:L / I:L / A:N** — bounded by what the Etherpad process can already touch; confidentiality is via secondary read-paths (the LibreOffice conversion error log can echo bytes from the symlinked file).

Single-tenant deployments where only the Etherpad operator has shell access on the host are not exposed.

## Affected versions

- All `ep_etherpad-lite` versions through `v3.0.0` (inclusive). The `Math.floor(Math.random() * 0xFFFFFFFF)` pattern is present in `src/node/handler/ImportHandler.ts` and `src/node/handler/ExportHandler.ts` for as far back as the repository history extends — older than the 2024-03-16 snapshot at commit [`107598b`](https://github.com/ether/etherpad/commit/107598b) where it first appears in the current file paths, and predating the v1.x era.

## Patched versions

- `ep_etherpad-lite >= 3.1.0` — the fix is on `develop` HEAD as commit `8c6104c`. Update this field with the actual tagged release version when it ships.

## Proof of concept (sketch)

```
# Pre-condition: attacker has shell on the same host as Etherpad,
# has read access to /tmp, and Etherpad's process can write to the
# chosen target (e.g. runs as root inside a Docker container).

# 1. Observe a temp filename from logs (or guess via prior exports).
TARGET=/etc/etherpad/SESSIONKEY.txt
GUESS=/tmp/etherpad_export_$(./predict-next-random)$EXT  # implementation-specific

# 2. Place the symlink before Etherpad creates the file.
ln -s "$TARGET" "$GUESS"

# 3. Trigger an export from the Etherpad UI (or via the API).
# Etherpad calls fs.writeFile(srcFile, ...) which open()s the symlink
# target with O_WRONLY|O_TRUNC and clobbers $TARGET with HTML content.
```

In practice the exact reproduction depends on the host's PRNG state predictability and the deployment's process-owner privileges. A reliable exploit chain needs `setpriv`-style host access or a sibling tenant.

## Workarounds

- Run Etherpad in a container with a private `/tmp` (Docker: `--tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m`, systemd: `PrivateTmp=true`).
- Ensure the Etherpad process does NOT run as root and has write access only to its own data directory.
- Set `TMPDIR` to an Etherpad-private directory in the environment.

## Fix

Patched in [`8c6104c`](https://github.com/ether/etherpad/commit/8c6104c) (PR [#7784](https://github.com/ether/etherpad/pull/7784)):

```diff
-const randNum = Math.floor(Math.random() * 0xFFFFFFFF);
+const randNum = crypto.randomBytes(16).toString('hex');
```

128 bits of CSPRNG entropy. Predicting the next filename is no longer feasible.

A bigger follow-up — per-request `mkdtemp` subdirectories with `O_EXCL`/`O_NOFOLLOW` semantics — is deferred to a later release; the immediate window (predictable 32-bit collisions across processes) is what the patch closes.

## Resources

- Patched in: https://github.com/ether/etherpad/pull/7784 (squash commit `8c6104c`).
- `Math.random()` is not appropriate for security-sensitive contexts. See the MDN guidance for [`Math.random()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random) and the Node.js recommendation to use [`crypto.randomBytes`](https://nodejs.org/api/crypto.html#cryptorandombytessize-callback) for unpredictable values.

## Credits

Reported during an internal security audit by Claude (via @JohnMcLear).

## References
- https://github.com/ether/etherpad/security/advisories/GHSA-2jwf-f4xq-f24h
- https://github.com/ether/etherpad/pull/7784
- https://github.com/ether/etherpad/commit/8c6104c5d5daf41f0d454acc04d42dffa0e0d996
- https://github.com/ether/etherpad
