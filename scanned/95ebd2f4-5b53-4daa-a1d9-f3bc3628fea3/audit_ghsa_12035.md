# [H] @grackle-ai/mcp has a workspace authorization bypass in its knowledge_search MCP tool

## Summary
Severity: High
Advisory: GHSA-647h-p824-99w7
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-647h-p824-99w7
Type: github-advisory

## Affected
- npm: `@grackle-ai/mcp` — affected >=0 <0.70.2

## Details
### Impact

The `knowledge_search` and `knowledge_get_node` MCP tools are included in `SCOPED_TOOLS` (visible to scoped agents) but their handlers do not receive `authContext` and do not enforce workspace scoping. A scoped agent in Workspace A can supply an arbitrary `workspaceId` parameter to search or retrieve knowledge graph nodes from Workspace B, bypassing workspace isolation boundaries.

This is a **cross-workspace data leakage** vulnerability affecting any deployment where multiple workspaces contain sensitive knowledge graph data and scoped agents are used.

**Affected code:**
- `packages/mcp/src/tools/knowledge.ts:146-169` (knowledge_search handler)
- `packages/mcp/src/tools/knowledge.ts:244-283` (knowledge_get_node handler)
- `packages/mcp/src/tool-scoping.ts:11` (both tools listed in SCOPED_TOOLS)

**Contrast with correct implementation:** `knowledge_create_node` (same file, lines 334-357) properly receives `authContext` and overrides the user-supplied `workspaceId` for scoped callers.

### Design Note

Cross-workspace knowledge sharing is a legitimate future feature — agents working across different repos may need to collaborate and share knowledge. However, this access should be **opt-in with explicit grants**, not an implicit bypass. The immediate fix locks scoped agents to their own workspace. A future design could introduce:
- Workspace-level "share knowledge with" settings
- A `cross_workspace` scope on scoped tokens
- Explicit `workspaceIds` (plural) in the auth context

### Patches

**Fix:** Add `authContext` parameter to `knowledge_search` and `knowledge_get_node` handlers and enforce workspace scoping, matching the pattern in `knowledge_create_node`:
```typescript
const resolvedWorkspaceId =
  authContext?.type === "scoped"
    ? authContext.workspaceId ?? ""
    : workspaceId ?? "";
```

When cross-workspace collaboration is designed, this check can be relaxed intentionally with proper access controls.

### Workarounds

Do not use scoped agent tokens in multi-workspace deployments until patched. Alternatively, remove `knowledge_search` and `knowledge_get_node` from the `SCOPED_TOOLS` set in `tool-scoping.ts`.

### References

- CWE-284: Improper Access Control
- File: `packages/mcp/src/tools/knowledge.ts`
- File: `packages/mcp/src/tool-scoping.ts`

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-647h-p824-99w7
- https://github.com/nick-pape/grackle
