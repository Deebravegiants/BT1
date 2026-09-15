# [C] 9routers has Exposure of Sensitive Information and Unprotected Database Import/Export, Allowing Complete Credential Theft and Database Takeover

## Summary
Severity: Critical
Advisory: GHSA-qvfm-67h2-2qfx
CVE: CVE-2026-55500
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-qvfm-67h2-2qfx
Type: github-advisory

## Affected
- npm: `9router` — affected >=0

## Details
## Summary

The `/api/settings/database` endpoint allows full database export (containing all credentials, API keys, OAuth tokens, and settings) and full database import (complete overwrite) without any authentication requirement beyond the `ALWAYS_PROTECTED` middleware check, which only validates JWT or CLI token. Combined with other vulnerabilities (e.g., default password, tunnel exposure), this enables complete database takeover.

## Description

The endpoint `/api/settings/database` is listed in `ALWAYS_PROTECTED` in `dashboardGuard.js` (line 42), which requires a valid JWT token or CLI token. However, this protection is insufficient because:

1. **GET (Export):** Returns the complete database including API keys (`key` field in `apiKeys` table), OAuth tokens, and all provider credentials. Line 80 in `src/lib/db/index.js`: `apiKeys: db.all("SELECT * FROM apiKeys").map(...)` — the `key` field contains the plaintext API key value.

2. **POST (Import):** Accepts arbitrary JSON and performs a complete database wipe-and-replace in a transaction (lines 102-163 in `src/lib/db/index.js`). This replaces all settings including the password hash, effectively allowing an attacker to set their own password.

3. The exported data includes `apiKeys` with their plaintext `key` values, `providerConnections` with all OAuth tokens, and `settings` with OIDC client secrets.

### Evidence

**File:** `src/app/api/settings/database/route.js`
```javascript
export async function GET() {
  const payload = await exportDb();
  return NextResponse.json(payload);
}

export async function POST(request) {
  const payload = await request.json();
  await importDb(payload);
  // ...
}
```

**File:** `src/lib/db/index.js` (lines 96-163)
```javascript
export async function importDb(payload) {
  db.transaction(() => {
    // Wipe all tables
    db.run(`DELETE FROM settings`);
    db.run(`DELETE FROM providerConnections`);
    db.run(`DELETE FROM providerNodes`);
    db.run(`DELETE FROM proxyPools`);
    db.run(`DELETE FROM apiKeys`);
    db.run(`DELETE FROM combos`);
    db.run(`DELETE FROM kv WHERE scope IN (...)`);
    // Then insert attacker-controlled data
    // ...
  });
}
```

The `exportDb` function at line 80 exposes API key plaintext:
```javascript
apiKeys: db.all(`SELECT * FROM apiKeys`).map((r) => ({ 
  id: r.id, key: r.key, name: r.name, ...
})),
```

## Steps to Reproduce

1. Authenticate with any valid JWT (e.g., using the default password "123456")
2. Export: `curl -b auth_token=<jwt> http://localhost:20128/api/settings/database`
3. Observe: Full database dump with all credentials in plaintext
4. Import malicious data: `curl -X POST -b auth_token=<jwt> -H "Content-Type: application/json" -d '<modified-db>' http://localhost:20128/api/settings/database`
5. All settings, passwords, API keys are now replaced with attacker-controlled values

## Impact

- **Confidentiality:** Complete exposure of all stored secrets (API keys, OAuth tokens, OIDC client secrets)
- **Integrity:** Complete database replacement with attacker-controlled data
- **Availability:** Database wipe is possible by importing an empty database
- **Scope Changed:** Importing new settings affects all users and downstream services

## Recommended Fix

1. Require re-authentication for database export/import (not just an existing session)
2. Mask/redact API keys in export (or require explicit opt-in for key export)
3. Add confirmation step for import (require current password verification)
4. Implement database backup before import
5. Log all export/import operations with audit trail

## References
- https://github.com/decolua/9router/security/advisories/GHSA-qvfm-67h2-2qfx
- https://github.com/decolua/9router
