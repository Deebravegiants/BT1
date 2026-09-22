# [M] Miniflux Media Proxy SSRF via /proxy endpoint allows access to internal network resources

## Summary
Severity: Medium
Advisory: GHSA-xwh2-742g-w3wp
CVE: CVE-2026-21885
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-xwh2-742g-w3wp
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=0 <2.2.16

## Details
### Summary
Miniflux's media proxy endpoint (`GET /proxy/{encodedDigest}/{encodedURL}`) can be abused to perform Server-Side Request Forgery (SSRF). An authenticated user can cause Miniflux to generate a signed proxy URL for attacker-chosen media URLs embedded in feed entry content, including internal addresses (e.g., localhost, private RFC1918 ranges, or link-local metadata endpoints). Requesting the resulting `/proxy/...` URL makes Miniflux fetch and return the internal response.

### Details
- **Vulnerable route**: `GET /proxy/{encodedDigest}/{encodedURL}` (accessible without authentication, but requires a server-generated HMAC-signed URL)
- **Handler**: `internal/ui/proxy.go` (`(*handler).mediaProxy`)
- **Trigger**: entry content is rewritten to proxy media URLs (e.g., `mediaproxy.RewriteDocumentWithAbsoluteProxyURL(...)`), producing signed `/proxy/...` URLs.
- **Root cause**: the proxy validates the URL scheme and HMAC signature, but does not restrict target hosts/IPs. As a result, requests to loopback/private/link-local addresses are allowed and fetched by the server.

### PoC
1) Run Miniflux 2.2.15 with default configuration (media proxy enabled by default: `MEDIA_PROXY_MODE=http-only`).

2) Log in with any normal user account.

3) Subscribe to a feed you control that contains an entry with an image URL pointing to an internal address reachable from the Miniflux server, e.g.:
   - `<img src="http://<internal-target>/secret">`
   (Note: `<internal-target>` must be reachable *from the Miniflux process/network*; in containerized setups, `127.0.0.1` may not refer to the host.)

4) Open the entry and locate the rewritten media proxy URL (`/proxy/<encodedDigest>/<encodedURL>`) in the rendered HTML/page source.

5) Request the `/proxy/...` URL.
Expected (vulnerable): Miniflux fetches the internal URL and returns the internal response (SSRF).

### Impact
**Type**: SSRF (Server-Side Request Forgery) via media proxy  
**Who is impacted**: Miniflux instances with media proxy enabled (default configuration typically enables it for HTTP/mixed content handling).  
**Impact**: attackers with a valid Miniflux account can fetch internal resources reachable from the Miniflux server (e.g., localhost services, private network services, and link-local endpoints such as 169.254.169.254), potentially exposing sensitive data.

### Suggested CVSS (v3.1)
`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` (Base 6.5)




If there any questions or issues reproducing this, please contact: jeongwoolee340@gmail.com

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-xwh2-742g-w3wp
- https://nvd.nist.gov/vuln/detail/CVE-2026-21885
- https://github.com/miniflux/v2
