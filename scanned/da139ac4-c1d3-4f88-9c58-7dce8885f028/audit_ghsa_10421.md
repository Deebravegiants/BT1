# [H] Paperclip: Unauthenticated Access to Multiple API Endpoints in Authenticated Mode

## Summary
Severity: High
Advisory: GHSA-xfqj-r5qw-8g4j
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xfqj-r5qw-8g4j
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
## Summary

Several API endpoints in `authenticated` mode have no authentication at all. They respond to completely unauthenticated requests with sensitive data or allow state-changing operations. No account, no session, no API key needed.

Verified against the latest version.

Discord: sagi03581

## Steps to Reproduce

### 1. Unauthenticated issue data access

`GET /api/heartbeat-runs/:runId/issues` returns issue data for a heartbeat run with zero authentication. Every other endpoint in `server/src/routes/activity.ts` calls `assertCompanyAccess`, but this one was missed.

```bash
curl -s http://<target>:3100/api/heartbeat-runs/00000000-0000-0000-0000-000000000001/issues
# -> []  (HTTP 200, not 401 or 403)
```

If an attacker obtains a valid run UUID (from logs, error messages, shared URLs, or by probing), they can read issue data without any credentials.

### 2. Unauthenticated CLI auth challenge creation

`POST /api/cli-auth/challenges` creates a CLI authentication challenge with no actor check at all. The handler at `server/src/routes/access.ts:1638-1659` skips any auth verification.

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"command":"test"}' \
  http://<target>:3100/api/cli-auth/challenges
# returns challenge ID, token, and a pre-generated board API key
```

The response includes a `boardApiToken` that becomes active once the challenge is approved. Combined with open registration (separate report), this enables persistent API key generation.

### 3. Unauthenticated agent instruction / system prompt leakage

These endpoints in `server/src/routes/access.ts` require no authentication:

```bash
curl -s http://<target>:3100/api/skills/index
# returns all available skill endpoints

curl -s http://<target>:3100/api/skills/paperclip
# returns the FULL agent heartbeat procedure including:
#   - every API endpoint and its parameters
#   - authentication mechanism (env var names, header formats)
#   - the complete agent coordination protocol
#   - the agent creation/hiring workflow

curl -s http://<target>:3100/api/skills/paperclip-create-agent
# returns the full agent creation workflow with adapter configs
```

This hands an attacker a complete map of the internal API without authenticating. It also leaks how agents authenticate, how heartbeats work, and what adapter configurations are available.

### 4. Unauthenticated deployment configuration disclosure

`GET /api/health` returns deployment mode, exposure setting, auth status, bootstrap status, version, and feature flags.

```bash
curl -s http://<target>:3100/api/health
# {
#   "deploymentMode": "authenticated",
#   "deploymentExposure": "public",
#   "authReady": true,
#   "bootstrapStatus": "ready",
#   "version": "2026.403.0",
#   ...
# }
```

Tells an attacker exactly how the instance is configured, whether registration is available, and what version is running.

## Impact

- **Data exposure**: heartbeat run issues accessible without credentials. Agent instructions and full API structure exposed to anyone.
- **Reconnaissance**: an attacker can fingerprint the deployment (mode, version, features) and map the entire internal API before attempting anything else.
- **Auth bypass stepping stone**: unauthenticated CLI challenge creation is a building block for the full RCE chain (reported separately).

## Suggested Fixes

1. **Add authentication to heartbeat run issues** in `server/src/routes/activity.ts`:
   - `GET /api/heartbeat-runs/:runId/issues` -- add `assertCompanyAccess` like every other endpoint in the same file

2. **Add authentication to CLI challenge creation** in `server/src/routes/access.ts`:
   - `POST /api/cli-auth/challenges` -- add `assertBoard` at minimum

3. **Add authentication to skill endpoints** in `server/src/routes/access.ts`:
   - `GET /api/skills/available`
   - `GET /api/skills/index`
   - `GET /api/skills/:skillName`

4. **Reduce health endpoint information** -- consider removing `deploymentMode`, `deploymentExposure`, and `version` from the unauthenticated response, or gating the full response behind `assertBoard`

5. Consider a **global auth rejection middleware** for all `/api/*` routes in `authenticated` mode. Currently unauthenticated requests get `actor: { type: "none" }` and pass through to `next()`, relying on each route handler to check individually. A missing check means an open endpoint. Rejecting `type: "none"` at the middleware level for all routes except an explicit public allowlist (health, sign-in, sign-up, webhooks) would prevent this class of bug entirely.

## Contact

Discord: sagi03581

Happy to help verify fixes or provide additional details.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-xfqj-r5qw-8g4j
- https://github.com/paperclipai/paperclip
