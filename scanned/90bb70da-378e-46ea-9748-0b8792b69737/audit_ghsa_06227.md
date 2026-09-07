# [H] Flowise: Missing Authorization on Execution Update Endpoint

## Summary
Severity: High
Advisory: GHSA-fm2f-4339-4p2f
CVE: CVE-2026-70475
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-fm2f-4339-4p2f
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
# Flowise Security Audit Report
**Date**: 2026-03-17
**Researcher**: Dimpal Jadhav (jadhavdimpy@gmail.com)
**GitHub**: https://github.com/Dimpyj1604
**Target**: FlowiseAI/Flowise (latest main branch)
**Version**: flowise-components@3.1.0

### FINDING 1: Missing Authorization on Execution Update Endpoint
**Severity**: HIGH (CVSS ~7.5)
**Type**: CWE-862 (Missing Authorization)
**File**: `packages/server/src/routes/executions/index.ts:11`

**Description**: The `PUT /api/v1/executions/:id` endpoint lacks the `checkAnyPermission()` middleware that protects all other execution endpoints (GET, DELETE). Any authenticated user — regardless of their assigned permissions — can modify any execution record.

**Evidence**:
```typescript
// Line 7 - GET has permission check
router.get('/', checkAnyPermission('executions:view'), executionController.getAllExecutions)

// Line 11 - PUT has NO permission check
router.put(['/', '/:id'], executionController.updateExecution)  // <-- MISSING checkAnyPermission

// Line 14 - DELETE has permission checkadvisory_1_execution_auth_bypass
router.delete('/:id', checkAnyPermission('executions:delete'), executionController.deleteExecutions)
```

**Impact**: Privilege escalation. A low-privileged user with any valid API key can modify execution state, data, and metadata of any execution in their workspace. Could be used to manipulate workflow execution results or inject data.

**Reproduction**:
```bash
curl -X PUT https://TARGET/api/v1/executions/EXECUTION_ID \
  -H "Authorization: Bearer LOW_PRIV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"state": "FINISHED", "data": "MANIPULATED"}'
```

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-fm2f-4339-4p2f
- https://github.com/FlowiseAI/Flowise/pull/6409
- https://github.com/FlowiseAI/Flowise/commit/96a9b23b5a103b362a0ee1368d04636755be1bed
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
