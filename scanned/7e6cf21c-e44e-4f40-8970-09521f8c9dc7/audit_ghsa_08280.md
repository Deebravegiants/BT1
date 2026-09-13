# [H] FlowiseAI Exposes Basic Auth Credentials via API

## Summary
Severity: High
Advisory: GHSA-php6-83fg-gw3g
CVE: CVE-2026-46440
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-php6-83fg-gw3g
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
**Detection Method:** Kolega.dev Deep Code Scan

| Attribute | Value |
|---|---|
| Severity | Medium |
| CWE | CWE-522 (Insufficiently Protected Credentials) |
| Location | packages/server/src/enterprise/controllers/account.controller.ts:128-135 |
| Practical Exploitability | Medium |
| Developer Approver | faizan@kolega.ai |

### Description
The checkBasicAuth endpoint validates credentials in plaintext without rate limiting and with direct comparison.

### Affected Code
```
public async checkBasicAuth(req: Request, res: Response) {
    const { username, password } = req.body
    if (username === process.env.FLOWISE_USERNAME && password === process.env.FLOWISE_PASSWORD) {
        return res.json({ message: 'Authentication successful' })
```

### Evidence
Credentials are sent in plaintext in request body and compared directly without hashing. No rate limiting prevents brute force attacks. The endpoint returns different messages for success/failure, enabling enumeration.

### Impact
Credential brute-forcing - attackers can attempt unlimited username/password combinations against the basic auth system. Successful attacks grant access to the application.

### Recommendation
1) Implement rate limiting on this endpoint, 2) Use constant-time comparison to prevent timing attacks, 3) Consider using hashed comparison, 4) Return generic error messages, 5) Add logging for failed attempts.

### Notes
The checkBasicAuth endpoint at line 128-135 has multiple security issues: (1) No rate limiting - the RateLimiterManager only applies to chatflow-specific endpoints, not auth endpoints. Attackers can perform unlimited brute force attempts. (2) Uses JavaScript === operator for comparison which is not constant-time, potentially enabling timing attacks. (3) Returns different messages for success ('Authentication successful') vs failure ('Authentication failed'), enabling credential enumeration. The endpoint compares plaintext credentials against environment variables FLOWISE_USERNAME and FLOWISE_PASSWORD. While this is basic auth for simpler deployments, the lack of rate limiting makes it actively exploitable for credential brute-forcing.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-php6-83fg-gw3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-46440
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
