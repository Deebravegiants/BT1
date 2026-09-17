# [H] FlowiseAI: Vector Store No Permission Checks

## Summary
Severity: High
Advisory: GHSA-hmg2-jjjx-jcp2
CVE: CVE-2026-46444
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-hmg2-jjjx-jcp2
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### FINDING 4: OpenAI Assistants Vector Store - No Auth on CRUD Operations
**Severity**: HIGH (CVSS ~8.1)
**Type**: CWE-306 (Missing Authentication for Critical Function)
**File**: `packages/server/src/routes/openai-assistants-vector-store/index.ts`

**Description**: ALL CRUD endpoints for OpenAI Assistants Vector Store have no authentication middleware AND the route path `/api/v1/openai-assistants-vector-store` is NOT in `WHITELIST_URLS`. However, it is also NOT protected by the main auth middleware when accessed via API key — the route requires API key auth (not whitelisted), but NO permission checks exist on any operation.

The real issue is that the routes have no `checkAnyPermission()` middleware, meaning any authenticated user regardless of role can:
- Create vector stores
- Upload files to vector stores
- Delete vector stores and files
- Modify any vector store

**Evidence**:
```typescript
// No permission middleware on any route
router.post('/', controller.createAssistantVectorStore)          // No permission check
router.put(['/', '/:id'], controller.updateAssistantVectorStore) // No permission check
router.delete(['/', '/:id'], controller.deleteAssistantVectorStore) // No permission check
router.post('/:id', getMulterStorage().array('files'), controller.uploadFilesToAssistantVectorStore) // No permission check
```

**Impact**: Any authenticated user can manipulate OpenAI vector stores, upload malicious files, delete data, or exfiltrate stored documents regardless of their assigned permissions.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-hmg2-jjjx-jcp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-46444
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
