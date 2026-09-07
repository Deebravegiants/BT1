# [C] S3-Proxy has Security Issues in its Resource Path Matching Implementation

## Summary
Severity: Critical
Advisory: GHSA-rfgq-wgg8-662p
CVE: CVE-2026-42882
CWE: CWE-22, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-rfgq-wgg8-662p
Type: github-advisory

## Affected
- Go: `github.com/oxyno-zeta/s3-proxy` — affected >=0 <0.0.0-20260424211602-1320e4abd46a

## Details
## Background

The original concern is functional: a resource pattern should treat a percent-encoded segment like some%2Fvalue as a single opaque token rather than splitting it into two path segments at the decoded /. Investigation into why %2F was being decoded and how routes matched against the result surfaced three related security issues, documented below.

Rather than landing a fix directly, the problem space warrants discussion first. Different fixes carry different compliance and compatibility tradeoffs, and every viable option is a breaking change in some form. Aligning on a direction before committing to an implementation is the safer path.

## Root cause: two different path representations

Go's `net/http` decodes percent-encoded characters when it parses an incoming URL:
`%2F` becomes `/` in `r.URL.Path`, while the original encoded form is preserved in
`r.URL.RawPath`. Two different parts of s3-proxy use different fields:

- The **auth middleware** calls `r.URL.RequestURI()`, which returns the encoded
  form (from `RawPath` when available). It sees `%2F` as literal characters, not
  as path separators.
- The **bucket handler** reads `r.URL.Path` to build the S3 key. It sees the
  decoded form, where `%2F` has already become `/`.

All three issues stem from this mismatch, combined with how glob patterns are
compiled. The examples below use PUT for concreteness, but the auth bypass applies
to any HTTP method — a config that restricts GET or DELETE on a namespace is
equally affected, meaning an attacker could read from or delete objects in a
protected namespace without credentials.

### A note on RFC 3986

RFC 3986 §2.2 states that `/` and `%2F` are **not equivalent** in a URI path:

> URIs that differ in the replacement of a reserved character with its
> corresponding percent-encoded octet are **not** equivalent.

`/` is a reserved gen-delim used as a path segment separator. `%2F` is its
percent-encoded form and, by the RFC, should be treated as data *within* a
segment — not as a separator. So:

- `/foo/bar/baz` → three segments: `foo`, `bar`, `baz`
- `/foo%2Fbar/baz` → two segments: `foo/bar` (opaque data), `baz`

The original functional concern (wanting `foo%2Fbar` to match as a single token
against a single-segment wildcard) is therefore RFC-correct behaviour. Go's
`r.URL.Path` violates this by decoding `%2F` to `/`, collapsing the two
representations into one. This is the underlying tension that makes fixing these
issues non-trivial: the simplest security fix makes s3-proxy *more* RFC
non-compliant, while the RFC-correct fix requires a more significant refactor.

### A note on breaking changes

Any of the proposed fixes for these issues should be treated as a **breaking
change**. Each option alters how path patterns in existing configs are interpreted
— whether by changing how `*` matches segments, by shifting which path
representation auth matches against, or by normalising paths before they reach the
router. Operators upgrading to a fixed version will need to review their resource
path definitions, and a clear migration note in the changelog is essential
regardless of which approach is chosen.

One way to avoid a hard breaking change would be to introduce a new field — for
example `route:` — that carries the fixed semantics, while keeping the existing
`path:` field with its current behaviour (and marking it deprecated). Operators
could migrate resource definitions incrementally, and the security fix would be
available immediately without requiring a coordinated config update across all
deployments. The obvious cost of this approach is maintaining two parallel
implementations, duplicated test coverage, and the ongoing burden of supporting
a deprecated code path until it can eventually be removed.

---

## Issue 1 — `*` in resource paths matches across `/`

### Background

Resource paths are matched using `github.com/gobwas/glob`. The call site is:

```go
// pkg/s3-proxy/authx/authentication/main.go
g, err := glob.Compile(res.Path)
```

`glob.Compile` is called **without a separator argument**. Without a separator,
`*` matches any character — including `/`. This means a pattern intended to protect
a single path segment actually matches across directory boundaries.

### Example

Consider a config with an open route and a protected route:

```yaml
resources:
  # open — no auth required
  - path: /upload/*/drafts/
    methods: [PUT]
    whiteList: true

  # protected — basic auth required
  - path: /upload/*/restricted/
    methods: [PUT]
    basic:
      ...
```

The intent is clear: `drafts` is open, `restricted` is protected. The `*` is meant
to match a single path segment (the object identifier).

However, because `*` crosses `/`, the pattern `/upload/*/drafts/` also matches:

```
PUT /upload/foo/drafts/../restricted/
```

The path segment matched by `*` is `foo`, and then `drafts/../restricted/` is
consumed by the rest of the pattern — because without a separator, `*` is equivalent
to `.*` and matches `/`, `.`, and everything else.

The result: an unauthenticated request is accepted by the open route.

### Fix discussion

The straightforward fix is to pass `'/'` as the separator to `glob.Compile`:

```go
// before
g, err := glob.Compile(res.Path)

// after
g, err := glob.Compile(res.Path, '/')
```

With a separator set:
- `*` matches any sequence of non-`/` characters (a single path segment).
- `**` matches any sequence including `/` (crossing path boundaries).

This fix closes the Issue 1 attack above: with a separator, `drafts/../restricted/`
is more than one segment and no longer matches the pattern `/upload/*/drafts/`.

#### Breaking change

Any existing config that relies on `*` crossing `/` must be updated to `**`. For
example:

```yaml
# before — worked accidentally because * crossed /
- path: /upload/*/drafts/

# after — single-segment match (behaviour unchanged for single-segment IDs)
- path: /upload/*/drafts/

# after — multi-segment match (e.g. nested object IDs containing /)
- path: /upload/**/drafts/
```

A migration note in the changelog would be needed.

---

## Issue 2 — Percent-encoded slashes bypass auth via segment collapsing

### Background

With Fix 1 applied, `*` only matches a single path segment. However, the auth
middleware matches against `r.URL.RequestURI()` — the **encoded** path — while the
bucket handler uses `r.URL.Path` — the **decoded** path. A client can use `%2F`
to make what looks like a single segment in the encoded URI decode into multiple
segments including a protected path component.

### Example

Using the same config as Issue 1:

```
PUT /upload/foo%2Frestricted/drafts/
```

Step by step:

1. `r.URL.RawPath` = `/upload/foo%2Frestricted/drafts/`
2. `r.URL.Path` (decoded) = `/upload/foo/restricted/drafts/`
3. Auth middleware calls `r.URL.RequestURI()` → returns the encoded form.
4. With Fix 1's separator `/`, glob splits on the literal `/`. The segment between
   the first and second slash is `foo%2Frestricted` — one token with no literal `/`
   — so `*` matches it. Pattern `/upload/*/drafts/` fires.
5. Open route → request proceeds without auth.
6. Bucket handler uses `r.URL.Path` → S3 key is `upload/foo/restricted/drafts/…`
   — **written into the restricted namespace without credentials**.

### Proof via integration test

I added `TestPercentEncodedSlashBypass` to
`pkg/s3-proxy/server/server_integration_test.go`. The test sends a complete
multipart PUT without credentials and asserts a 401 response. It currently fails
with **204** — the file is written in full to the restricted namespace without any
authentication.

### Fix discussion

This issue has two fundamentally different classes of fix, each with a different
stance on RFC 3986 compliance.

#### Option A — Match auth against the decoded path (`r.URL.Path`)

Change the auth middleware to use `r.URL.Path` instead of `r.URL.RequestURI()`:

```go
// before
requestURI := r.URL.RequestURI()

// after
requestURI := r.URL.Path
```

Both auth and the bucket handler now operate on the same decoded string, closing
the mismatch that enables the bypass.

**Pros:** One-line change; no other code touched; closes the bypass completely.

**Cons:** RFC 3986 non-compliant — `/foo%2Fbar/baz` and `/foo/bar/baz` become
indistinguishable at the auth layer. A pattern like `/upload/*/drafts/` will match
both `PUT /upload/foo/drafts/` and `PUT /upload/foo%2F.../drafts/` identically
after decoding, making it impossible for operators to write a pattern that
distinguishes the two. Any path segment containing a literal `/` encoded as `%2F`
can never be matched as a single token by `*`.

#### Option B — Use the raw path in both auth and key construction

Keep `r.URL.RequestURI()` in the auth middleware (reverting the Option A change)
and replace the bucket handler's decoded path extraction with `r.URL.EscapedPath()`
stripped of the mount path prefix. The AWS SDK then handles percent-encoding the
key in the HTTP request to S3, with no manual segment splitting required.

This keeps `%2F` opaque at both layers: auth matches against the encoded form, and
the S3 key preserves the encoded characters verbatim.

**Security mechanism:** the bypass attack (`PUT /upload/foo%2Frestricted/drafts/`)
still returns **204** — the open route genuinely matches, because
`foo%2Frestricted` is one encoded segment and `*` accepts it. However, the key
written to S3 is `upload/foo%2Frestricted/drafts/…` — a distinct namespace from
`upload/foo/restricted/drafts/…`. The attacker cannot reach the protected prefix
because `%2F` and `/` are treated as different characters all the way to storage.

**AWS S3 compatibility confirmed:** S3 natively supports `%2F` in key names. A
key `upload/foo%2Fbar/file.txt` is stored and retrieved as a distinct object from
`upload/foo/bar/file.txt`. All four operations (HEAD, GET, PUT, DELETE) work
correctly with `%2F`-containing paths.

**Pros:** RFC-compliant; `%2F` remains a meaningful encoding — `foo%2Fbar` is one
token and `*` correctly matches it as a single segment; `/foo%2Fbar/baz` and
`/foo/bar/baz` are distinct at both auth and storage layers; simpler than it
sounds — no custom segment-splitting utility needed, just `r.URL.EscapedPath()` in
the handler.
The breaking change is **contained to config files, not clients**: the only clients that break
are those relying on `*` crossing literal `/` — and those require a config change
to `**` under any fix option. Clients that encode user input containing `/` as
`%2F` in a path segment are preserved: `foo%2Fbar` is still one encoded segment,
and `*` still matches it. Under Option A those same clients break — the decoded
form splits into multiple segments that no longer match `*`. The required
client-side fix would be to filter or transform any `/` out of user input before
building the URL, which may not always be feasible if the `/` carries meaning.

**Cons:** The auth middleware reverts to using the encoded path, which re-opens
the door to dot-segment bypass (Issue 3) if the path-cleaning middleware is not
also in place — the two fixes must be applied together.

A note on the 204 response: a request like `PUT /upload/foo%2Frestricted/drafts/`
returns 204 under this option, which may look like a bypass at first glance. It is
not. If `%2F` carries meaning, `foo%2Frestricted` is a valid identifier
indistinguishable from any other — the server has no basis to treat it as
suspicious. The correct security responsibility is to handle all inputs
consistently and safely, not to guess intent based on the content of user-provided
values. The namespace separation guarantee satisfies that: whatever the client
sends is handled the same way at both the auth and storage layers.

#### Option C — Reject requests containing `%2F` in the path

Return 400 Bad Request for any request whose raw path contains `%2F`:

```go
if strings.Contains(r.URL.RawPath, "%2F") || strings.Contains(r.URL.RawPath, "%2f") {
    http.Error(w, "Bad Request", http.StatusBadRequest)
    return
}
```

**Pros:** Simplest possible enforcement; eliminates the ambiguity entirely.

**Cons:** Breaks any client that sends object names containing `/` encoded as
`%2F`; rules out a legitimate and RFC-sanctioned use of percent-encoding.

---

## Issue 3 — Dot-dot segments bypass authentication with prefix patterns

### Background

Issues 1 and 2 both involve `*` (single-segment wildcard). A different class of
bypass survives Fix 1 and Fix 2 when configs use prefix-style patterns with `**`
at the end, such as `/open/**`. This is a natural and common pattern for "allow
everything under this prefix." The `**` token is explicitly designed to cross `/`,
so `..` traversal within that prefix still reaches protected paths.

Note that `%2F..%2F` encoded traversal is a variant of this issue: the decoded
form (`/../`) contains dot segments that `**` can consume, as described in the
root cause section.

### Example

Consider this config:

```yaml
resources:
  # protected — basic auth required for anything under /restricted/
  - path: /restricted/**
    methods: [PUT]
    basic:
      ...

  # open — no auth required for anything under /open/
  - path: /open/**
    methods: [PUT]
    whiteList: true
```

Without any path normalization, the following request bypasses auth:

```
PUT /open/../restricted/secret.json
```

Step by step:

1. Go's `net/url` resolves dot segments when parsing the request URI: `r.URL.Path`
   is `/restricted/secret.json`. The raw form `../` is preserved only in
   `r.URL.RawPath`.
2. The auth middleware calls `r.URL.RequestURI()`, which returns the encoded
   form — `/open/../restricted/secret.json` — and evaluates resources against that.
3. `/restricted/**` does not match because the raw path does not start with `/restricted/`.
4. `/open/**` matches: `**` is allowed to cross `/`, so it consumes `../restricted/secret.json`.
5. The open route fires — no auth required — the request returns 204.
6. The bucket handler reads `r.URL.Path` — already `/restricted/secret.json` — and
   writes the file directly into the restricted namespace.

**Confirmed against AWS S3**: the file lands at `restricted/secret.json` — not at
a key containing `../`. Go resolves the dot segments before the bucket handler runs,
so the write goes straight into the protected prefix. This makes the attack more
severe than a key-naming anomaly: it is a direct, confirmed write into the
restricted namespace with no authentication.

### Proof via integration test

I added `TestPathTraversalDoubleStarPrefix` to
`pkg/s3-proxy/server/server_integration_test.go`. It uses the exact config above
and shows that, with a path-cleaning middleware applied **before** the auth
middleware, the traversal returns 401 instead of 204:

```go
{
    // /open/** still matches /open/../restricted/file because ** crosses '/'.
    // cleanPathMiddleware resolves the path to /restricted/file first, which
    // matches the protected resource -> 401.
    // Without cleanPathMiddleware this would return 204 (auth bypassed).
    name:         "traversal from open to restricted via ** prefix pattern is blocked",
    inputMethod:  "PUT",
    inputURL:     "http://localhost/open/../restricted/file.txt",
    expectedCode: 401,
},
```

### Note on `%2E` (percent-encoded dots)

Go's `net/http` decodes `%2E` → `.` in `r.URL.Path` before any middleware runs,
so `%2E%2E` arrives as `..` by the time any of the options below apply. All options
operate on the already-decoded `r.URL.Path` and therefore handle encoded dots
without any extra work.

### Fix discussion

All options below address the same root problem: `r.URL.RequestURI()` preserves
dot segments while `r.URL.Path` has already resolved them, and auth sees the
un-resolved form. The options differ in where the resolution happens and how
invasive the change is.

#### Option A — Reject requests containing dot segments

Reject (400 Bad Request) any request whose decoded path contains `/./` or `/../`:

```go
func rejectDotSegmentsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        p := r.URL.Path
        if strings.Contains(p, "/./") || strings.Contains(p, "/../") ||
            strings.HasSuffix(p, "/.") || strings.HasSuffix(p, "/..") {
            http.Error(w, "Bad Request", http.StatusBadRequest)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

**Pros:** Simple, explicit, no normalization side-effects.  
**Cons:** Rejects requests that some clients may legitimately send (though dot
segments in HTTP paths are unusual and ill-advised).

#### Option B — Use `path.Clean`

```go
func cleanPathMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        p := r.URL.Path
        cleaned := path.Clean(p)
        if cleaned != p {
            r2 := r.Clone(r.Context())
            r2.URL.Path = cleaned
            r2.URL.RawPath = ""
            next.ServeHTTP(w, r2)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

`path.Clean` resolves `..` and `.`, collapses double slashes, and also removes
the trailing slash. The trailing-slash removal is a breaking change for any config
that uses paths ending in `/` — resource patterns, mount paths, or anything else
matched against the incoming path. A request to `/upload/foo/drafts/` would be
cleaned to `/upload/foo/drafts`, and any pattern or handler that expects the
trailing slash would no longer match.

This can be mitigated by restoring the trailing slash after cleaning:

```go
if len(p) > 1 && p[len(p)-1] == '/' {
    cleaned += "/"
}
```

**Implementation note:** An approach that stores the cleaned path in the request
context rather than modifying `r.URL.Path` and clearing `r.URL.RawPath` will not
work: both the auth middleware and the bucket handler read from `r.URL` directly,
so a context-stored override is invisible to them.

**Pros:** Uses the standard library; less custom code.  
**Cons:** The trailing-slash removal is mitigable by restoring the trailing slash
after cleaning (as shown above), but it adds a correctness requirement to the
middleware that is easy to overlook — omitting it silently breaks any config using
trailing-slash patterns, which is the default convention in s3-proxy examples and
documentation.

---

## Interaction between Issue 2 and Issue 3 fixes

The choice made for Issue 2 affects the tradeoffs for Issue 3:

- If **Option A** is chosen for Issue 2 (auth uses `r.URL.Path`), then dot segments
  have already been resolved by Go before any middleware runs, so Issue 3 is
  partially addressed without any additional middleware — but Option A's RFC
  non-compliance tradeoff still applies.
- If **Option B** is chosen for Issue 2 (raw path in both layers), the auth
  middleware sees the encoded form, which still contains literal `../` dot segments.
  Issue 3 is **not** addressed by Option B alone — one of the Issue 3 options must
  also be applied. Importantly, whichever dot-segment option is chosen must clear
  `r.URL.RawPath` when it modifies the path, so that `r.URL.EscapedPath()` in the
  bucket handler reflects the cleaned path. This works naturally with both Issue 3
  options (which operate on `r.URL.Path` and clear `RawPath`), and the fixes
  compose cleanly in practice.
- In all cases, an explicit dot-segment policy (reject or resolve) is clearer than
  relying on Go's implicit resolution as a side-effect.

---

## Combined effect

| Attack | Issue 1 fix | Issue 2 fix | Issue 3 fix |
|---|---|---|---|
| `*` crosses `/` (`/upload/*/drafts/` matches `../restricted/`) | Fixed | — | — |
| `%2F` segment injection (`foo%2Frestricted/drafts/` bypasses `*/restricted/`) | No | Fixed | — |
| `..` traversal via `**` prefix pattern (`/open/../restricted/`) | No | No | Fixed |
| `%2F..%2F` encoded traversal (decoded `..` consumed by `**`) | No | Fixed* | Fixed |

\* Issue 2's fix (auth using decoded path, Option A) also prevents `%2F`-encoded
dot segments from being treated as opaque tokens, so the decoded `..` is visible
to the glob before matching.

---

## Suggested combination of fixes

- **Issue 1:** Pass `'/'` as the separator to `glob.Compile`. Unambiguously correct; `*` should never have crossed `/`.
- **Issue 2:** Option B — use the raw path (`r.URL.EscapedPath()`) in both the auth middleware and the bucket handler. This is the only option that avoids client-side breaking changes for operators whose clients encode user input containing `/` as `%2F`. The security guarantee is namespace separation, which is the right model: the server has no basis to distinguish a legitimate `%2F`-encoded identifier from one that "looks like" a traversal attempt, so consistent handling at both layers is the correct responsibility boundary.
- **Issue 3:** Option B — `cleanPathMiddleware` using `path.Clean` with trailing slash restored. Required when using Issue 2 Option B, since auth still sees the raw path. The two fixes compose cleanly: the middleware modifies `r.URL.Path` and clears `r.URL.RawPath`, so `r.URL.EscapedPath()` in the bucket handler reflects the cleaned path.

The combined breaking change is limited to config files: operators need to replace `*` with `**` wherever multi-segment wildcard matching is intended. Client-facing URLs require no changes.

---


## Resources

- `pkg/s3-proxy/authx/authentication/main.go` — `findResource`, the `glob.Compile` call
- `pkg/s3-proxy/server/server_integration_test.go` — `TestPercentEncodedSlashBypass`, `TestPathTraversalDoubleStarPrefix`, `TestPathCleaning`
- `github.com/gobwas/glob` — separator documentation
- RFC 3986 §2.2 — equivalence of percent-encoded reserved characters
- RFC 3986 §3.3 — path segment semantics
- RFC 3986 §5.2.4 — dot-segment resolution in URI paths

## References
- https://github.com/oxyno-zeta/s3-proxy/security/advisories/GHSA-rfgq-wgg8-662p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42882
- https://github.com/oxyno-zeta/s3-proxy/commit/1320e4abd46ad18c2851fedde50dbb79df8b7a51
- https://github.com/oxyno-zeta/s3-proxy/commit/af5ff57d8c6022459495b8fb50130073bca7b48a
- https://github.com/oxyno-zeta/s3-proxy
