# [M] Cloudreve: Broken Access Control in file event stream: a single-file share recipient is subscribed to the owner's parent folder and receives activity events for unshared siblings

## Summary
Severity: Medium
Advisory: GHSA-w8x7-h2px-xmq8
CVE: CVE-2026-55499
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-w8x7-h2px-xmq8
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260613030215-0b00dd308f13
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary
 
When an authenticated recipient of a **single-file** share opens the file event stream (`GET /api/v4/file/events?uri=<share-root>`), Cloudreve validates the URI by listing it and then subscribes the caller to `parent.ID()`. For a single-file share, the share navigator resolves the bare share-root URI to the **owner-side parent folder** of the shared file (not the file), while the visible listing is filtered down to just the shared file. The event hub then keys topics by numeric file ID only and, on each file change, fans the event out to subscribers of **every ancestor topic**, filtering only the client ID that caused the event — never the subscriber's share scope.
 
Consequently, a recipient of one shared file can receive Server-Sent Events (type, sibling path/name, rename target, hashed file ID) for other files and subfolders in the owner's parent folder that were never shared. Contents are not disclosed; file-activity metadata is.

### Details
## Root cause (verified at `26b6b10`)
 
**1. Events route — authenticated, feature-flagged, no share-scope check** (`routers/router.go`):
```go
file := v4.Group("file"); file.Use(middleware.RequiredScopes(types.ScopeFilesRead))
file.GET("events",
    middleware.LoginRequired(),
    middleware.IsFunctionEnabled(func(c *gin.Context) bool { return dep.SettingProvider().EventHubEnabled(c) }),
    controllers.FromQuery[explorer.ExplorerEventService](...), controllers.HandleExplorerEventsPush)
```
`EventHubEnabled` defaults `true` (`inventory/setting.go: "fs_event_push_enabled":"1"`).
 
**2. Service subscribes to the listed parent's ID** (`service/explorer/events.go`):
```go
parent, _, err := m.List(c, uri, &manager.ListArgs{Page:0, PageSize:1})   // also runs share validity/password
...
rx, resumed, err := eventHub.Subscribe(c, parent.ID(), requestInfo.ClientID)
```
 
**3. Single-file share `Root` swaps the share root to the owner parent** (`share_navigator.go`):
```go
n.shareRoot = newFile(nil, share.Edges.File)
...
if n.shareRoot.Type() == types.FileTypeFile {
    n.singleFileShare = true
    n.shareRoot = n.shareRoot.Parent   // <-- owner-side parent folder
}
```
 
**4. `To` returns that parent for the bare root URI** (`share_navigator.go`):
```go
elements := path.Elements()
if len(elements) == 1 && n.singleFileShare { return latestSharedSingleFile(...) } // only when URI names the file
...
return current  // current == shareRoot == owner parent folder
```
The bare root share URI has **zero** path elements (`URI.Elements()` returns nil for path `/`), so the `len(elements)==1` guard is skipped and `To` returns the parent folder. `dbfs.List` returns that as `parent`, so `parent.ID()` is the owner parent folder's real ID.
 
**5. `Children` masks the broader parent** — for `singleFileShare` it returns only `[]*File{sharedFile}`, so the recipient's listing shows just the shared file even though the subscribed topic is the whole parent.
 
**6. Publication fans out to ancestor topics with only a client-ID filter** (`dbfs/events.go`):
```go
func (f *DBFS) getEligibleSubscriber(ctx, file, checkParentPerm) []foundSubscriber {
    roots := file.Ancestors()
    for _, root := range roots {
        subscribers := f.eventHub.GetSubscribers(ctx, root.Model.ID)
        subscribers = lo.Filter(subscribers, func(s eventhub.Subscriber, _ int) bool {
            return !(requestInfo != nil && s.ID() == requestInfo.ClientID)  // ONLY exclude the causing client
        })
        ...
    }
}
// emit*: From: subscriber.relativePath(file)  // owner-side path of the changed sibling
```
`relativePath` trims the changed file's owner path by the subscribed root's owner path, yielding the sibling's name (e.g. `/Secret-Plan.pdf`). No check that the subscriber is authorized for the changed file or within their share scope.
 
## Validation performed
 
Independent validation against commit `26b6b10` in a clean sandbox.
 
**Source-verified (static):** all of (1)–(6) confirmed verbatim, including the negative direction (an explicit `…/shared.txt` URI resolves to the file, and `oss`/`qiniu`-style flows are irrelevant here).
 
**Dynamic (control-flow executed):** the full binary is not buildable offline (modules behind an unreachable proxy, embedded frontend, DB/eventhub). The reseacher ran two harnesses:
- A `net/url`-based check of the linchpin — the bare root share URI yields `0` path elements (so `To` returns the parent), while `…/shared.txt` yields `1` (returns the file). This is the subtle point on which the whole finding turns, and it holds.
- A model of `Root`/`To`/`getEligibleSubscriber`/`relativePath` driving the end-to-end flow:
```
[1] single-file share root URI -> m.List parent = "docs" (id 10), NOT shared.txt (id 11)  -> subscribed to owner parent
[2] owner renames /docs/Secret-Plan.pdf -> client 'attacker' receives: from="/Secret-Plan.pdf" file_id=12 (topic 10)
[3] CONTROL: event caused by attacker's own client id -> suppressed (the only filter)
[4] CONTROL: explicit URI 'shared.txt' -> resolves to file (id 11) -> no sibling events
```

## Steps to reproduce
 
1. Owner shares a single file `shared.txt` from `/docs`, which also contains `Secret-Plan.pdf`.
2. Recipient (logged-in, `Files.Read`, with the share password if any) opens the event stream on the share root:
   ```
   GET /api/v4/file/events?uri=cloudreve%3A%2F%2F<share-id>%40share
   Cookie: cloudreve-session=<recipient-session>
   X-Cr-Client-Id: <uuid>
   Accept: text/event-stream
   ```
3. Owner creates/renames/modifies/moves/deletes `Secret-Plan.pdf`.
4. The recipient's stream receives, e.g.:
   ```
   event: event
   data: {"type":"rename","file_id":"<hashed>","from":"/Secret-Plan.pdf","to":"/Secret-Plan-v2.pdf"}
   ```
 
**Expected:** the recipient only receives events for the shared file.
**Actual:** the recipient receives activity events for unshared siblings in the owner's parent folder.
 
## Impact
 
A single-file share recipient gains a real-time feed of file-activity metadata for the owner's parent folder — sibling names, operation types, and rename targets they were never granted access to. No file contents are exposed.
 
## Remediation
 
- For single-file shares, subscribe to the shared file's ID, or reject event subscriptions on the single-file share root view.
- Store an authorization scope (navigator/share root) per subscriber and publish only events whose path stays within that scope.
- Incorporate user/share scope into topic keys, not just file ID + client ID.
- On subscriber reactivation, re-verify the requester still matches the subscriber and is authorized for the topic.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-w8x7-h2px-xmq8
- https://github.com/cloudreve/cloudreve/commit/0b00dd308f132d6e6e8476857ef79f4865600bbc
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.17.0
