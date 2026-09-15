# [M] SiYuan: getEncryptedNotebookStatus discloses names and current lock/unlock state of all encrypted notebooks to anonymous readers

## Summary
Severity: Medium
Advisory: GHSA-f2rw-w22v-54vh
Aliases: CVE-2026-72797, GO-2026-6414
Ecosystem: Go
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-f2rw-w22v-54vh
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724123622-8fb1b5766093

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72797](https://nvd.nist.gov/vuln/detail/CVE-2026-72797).

### Summary

`POST /api/notebook/getEncryptedNotebookStatus` returns the identifier, name, and current lock state of every encrypted notebook, with no publish-access filtering. The route is registered `CheckAuth` only, no `CheckReadonly`, no `CheckAdminRole` so it is reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. Encrypted notebooks are private by design; their names frequently reveal the sensitive topic that motivated encrypting them.

### Details

Route registration (`kernel/api/router.go:131`):
```go
ginServer.Handle("POST", "/api/notebook/getEncryptedNotebookStatus", model.CheckAuth, getEncryptedNotebookStatus)
```

The handler (`kernel/api/notebook.go`) accepts no arguments and contains no `IsReadOnlyRoleContext` branch and no publish-access filter of any kind. It returns, for every encrypted notebook, `{id, name, unlocked}`, the notebook's `box.Name` and its live lock state together with `enabled`, `count`, `migrationPending`, `migrationBoxes`, and `hasHistoryDependency`.

**Guarded-sibling asymmetry.** The primary notebook listing `lsNotebooks`, in the same file and also reader-reachable, *does* filter: it skips notebooks that are `Closed` and any notebook whose `publishAccess` entry is not `Visible`. The project therefore publish-scopes notebook listings but `getEncryptedNotebookStatus` enumerates all encrypted notebooks unconditionally.

**Still unfixed at HEAD.** The encrypted-notebook hardening series (issue #18034 idle auto-lock, lock-on-background, key handling, atomic unlock) is local-threat work. Commit `f2d966659` ("Expose encrypted notebook unlock status to plugins") introduced this exposure, and no subsequent commit gates it for the publish/reader boundary.

**Secondary effect.** `unlocked: true` is a live indicator of exactly when an encrypted notebook's plaintext is resident in memory, the window during which reader-reachable code paths that accept a notebook argument can read its decrypted content.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. At least one encrypted notebook exists.

```
POST http://127.0.0.1:6808/api/notebook/getEncryptedNotebookStatus
{}
```

Returns the full set of encrypted notebooks with their IDs, names, and current `unlocked` state including notebooks that `lsNotebooks` withholds from the same reader session. No arguments and no privileged access are required.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` learns which encrypted notebooks exist, what they are called, and whether each is currently unlocked. Notebook names are themselves sensitive: a user encrypts a notebook precisely because its subject matter is private, and the name commonly states that subject. Disclosing existence and naming to unauthenticated parties defeats that expectation, and the live lock state additionally reveals when the notebook's contents are decrypted in memory. Confidentiality-only.

### Suggested fix

For `IsReadOnlyRoleContext` sessions, either reject the request or restrict the response to notebooks that are publish-visible, mirroring the filtering already applied in `lsNotebooks`. Encrypted notebooks arguably should never be enumerated to a reader at all.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-f2rw-w22v-54vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-72797
- https://github.com/siyuan-note/siyuan/commit/8fb1b5766093371f6a516c221c92026b904fe779
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-getencryptednotebookstatus
