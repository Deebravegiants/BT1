# [H] Flowise: Unauthenticated OAuth 2.0 Access Token Disclosure via Public Chatflow in Flowise

## Summary
Severity: High
Advisory: GHSA-6f7g-v4pp-r667
CVE: CVE-2026-41273
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-6f7g-v4pp-r667
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary
Flowise contains an authentication bypass vulnerability that allows an unauthenticated attacker to obtain OAuth 2.0 access tokens associated with a public chatflow.

By accessing a public chatflow configuration endpoint, an attacker can retrieve internal workflow data, including OAuth credential identifiers, which can then be used to refresh and obtain valid OAuth 2.0 access tokens without authentication.

### Details
Flowise is designed to allow public chatflows to be accessed by unauthenticated end users via public URLs or embedded widgets. As a result, `chatflowId` values are intentionally exposed to unauthenticated clients and must not be treated as secrets.

However, the endpoint `GET /api/v1/public-chatbotConfig/<chatflowId>` returns internal `flowData` without authentication. The returned `flowData` includes workflow node definitions containing OAuth credential identifiers (`credential` field).

Separately, the endpoint `POST /api/v1/oauth2-credential/refresh/<credentialId>` allows OAuth. 2.0 tokens to be refreshed without authentication or authorization checks.

Because credential identifiers can be obtained from the unauthenticated public chatflow configuration endpoint, these two behaviors can be combined to allow unauthenticated OAuth 2.0 access token disclosure.

### PoC
**Prerequisites**
- Self-hosted Flowise instance
- A public chatflow configured with an OAuth 2.0 credential (e.g., Gmail OAuth2)

#### Step 1: Obtain `chatflowId`
The `chatflowId` is exposed to unauthenticated users via public chatflow URLs, embedded widgets, or browser network requests when accessing a public chatflow.

Example: `d37b9812-72c1-4c64-b152-665f307f755e`

#### Step 2: Retrieve internal `flowData` without authentication

```bash
curl -s \
  http://localhost:3000/api/v1/public-chatbotConfig/d37b9812-72c1-4c64-b152-665f307f755e
```

The response includes flowData containing an OAuth credential identifier, for example:

```
"credential": "6efe0e20-ba6f-4fbb-9960-658feffa0542"
```

#### Step 3: Refresh OAuth 2.0 token without authentication

```bash
curl -X POST \
  http://localhost:3000/api/v1/oauth2-credential/refresh/6efe0e20-ba6f-4fbb-9960-658feffa0542
```

The response returns valid OAuth 2.0 access token data, including an `access_token`.

### Impact
An unauthenticated attacker can obtain OAuth 2.0 access tokens for third-party services configured in Flowise, potentially leading to unauthorized data access, API abuse, or account compromise.

This vulnerability affects self-hosted deployments because public chatflows are commonly exposed to the internet and require unauthenticated access by design. Treating `chatflowId` as a secret does not mitigate the issue.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-6f7g-v4pp-r667
- https://nvd.nist.gov/vuln/detail/CVE-2026-41273
- https://github.com/FlowiseAI/Flowise
