# [M] Traefik: ForwardAuth identity spoofing via dot-form header alias

## Summary
Severity: Medium
Advisory: GHSA-rf44-j88r-hh8c
Aliases: CVE-2026-88011, CVE-2026-88879
Ecosystem: Go
Published: 2026-09-10
Source: https://osv.dev/vulnerability/GHSA-rf44-j88r-hh8c
Type: osv

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.56
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0 <3.7.12

## Details
## Summary

There is a medium severity vulnerability in Traefik's handling of request headers whose name aliases another header name. Go canonicalizes header names on dashes only, so `X-Auth-User`, `X_Auth_User` and `X.Auth.User` are three distinct headers to Traefik, while backends that derive variable names from header names (CGI, WSGI, PHP, NGINX, and others) collapse all of them into the same variable. A client can therefore smuggle an alias of a header that Traefik manages past the middleware managing it — for example a dot-form `X.Authenticated.User` alongside the canonical `X-Authenticated-User` written by the ForwardAuth middleware — and have such a backend read the client-supplied value instead of the identity Traefik asserted. Any header Traefik sets is exposed, not only ForwardAuth's. This is an incomplete-fix sibling of GHSA-x677-9fxg-v5c5, which blocked only the underscore form.

The mitigation is the new `aliasHeadersStrategy` entry point option. It defaults to `keep`, which preserves the previous behavior for backwards compatibility, so it must be explicitly set to `delete` or `reject` to take effect.

Traefik v1.x, the v2 releases up to v2.11.55 and the v3 releases from v3.0.0 to v3.7.11 are affected. The unmaintained lines among them will not receive a patch of their own, and the remedy for their users is to upgrade to v2.11.56 or v3.7.12 and set `aliasHeadersStrategy`.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.56
- https://github.com/traefik/traefik/releases/tag/v3.7.12

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
Traefik's ForwardAuth middleware removes the configured canonical identity header before copying the value returned by the auth service. However, a client-supplied dot-form alias such as `X.Authenticated.User` survives both this replacement and `underscoreHeadersStrategy: delete`.

The tested PHP 8.2 built-in SAPI maps `X-Authenticated-User` and `X.Authenticated.User` to the same `HTTP_X_AUTHENTICATED_USER` server variable. In Traefik's tested HTTP/1 backend path, the client value is serialized last and overrides the identity asserted by ForwardAuth.

A client whom ForwardAuth permits as a lower-privilege identity can therefore be treated by the backend as another user or role.

### Details
At `v3.7.10`, `pkg/server/server_entrypoint_tcp.go:800-818` removes or rejects only names containing `_`. After successful authentication, `pkg/middlewares/auth/forward.go:314-326` deletes and replaces only the canonical `authResponseHeaders` key. The dot alias remains in `req.Header` and the standard reverse proxy forwards both legal field names.

Go's HTTP/1 writer sorts header names lexically, placing `X-Authenticated-User` before `X.Authenticated.User`. PHP then collapses both into one `$_SERVER` key, so the attacker value deterministically wins.

This is an incomplete-fix sibling of `GHSA-x677-9fxg-v5c5`: the published underscore input is blocked by the new entry-point strategy, while the dot input bypasses that mitigation on the current stable release.

### PoC
[traefik-dot-forwardauth-poc.zip](https://github.com/user-attachments/files/30898195/traefik-dot-forwardauth-poc.zip)

run:
```bash
docker compose up -d
bash verify.sh
docker compose down
```

The decisive request is:

```http
GET /probe HTTP/1.1
Host: 127.0.0.1:18080
X.Authenticated.User: admin
Connection: close
```

Expected backend identity: `lab-user`, as returned by ForwardAuth.

Observed on `v3.7.10`: `admin`.

The script also verifies that requests without the alias, with the canonical header, and with the already-fixed underscore alias all produce `lab-user`.

### Impact
Applications that authorize requests using a ForwardAuth-provided identity header can receive an attacker-selected username or role instead. This was runtime-verified with PHP 8.2.27 and 8.2.33; impact on other normalization-prone backends is conditional. A lower-privilege permitted client may consequently impersonate another user or administrative role, affecting confidentiality and integrity.

This report does not claim bypass of a ForwardAuth denial: the auth service must first permit the request.


</details>
---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-rf44-j88r-hh8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-88011
- https://github.com/traefik/traefik/pull/13720
- https://github.com/traefik/traefik/commit/0331801c72329e0eaeb850e53ccce87c57fbecf8
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.56
- https://github.com/traefik/traefik/releases/tag/v3.7.12
