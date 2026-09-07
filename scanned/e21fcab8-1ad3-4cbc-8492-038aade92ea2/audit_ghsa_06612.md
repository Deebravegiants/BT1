# [M] @dynatrace-oss/dynatrace-mcp-server has a DQL injection via parameters not documented as DQL

## Summary
Severity: Medium
Advisory: GHSA-pqh8-p93p-2rx7
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-pqh8-p93p-2rx7
Type: github-advisory

## Affected
- npm: `@dynatrace-oss/dynatrace-mcp-server` — affected >=0 <2.1.1

## Details
### Summary
A DQL injection vulnerability in several read tools lets a caller bypass the tools' documented field-scope, time-window, and display caps by injecting DQL pipeline stages through parameters typed as identifiers.

### Details
Several tools interpolate caller-supplied parameters directly into DQL query strings without quoting or escaping. The affected parameters are documented in their Zod schemas as identifiers or constrained shorthand (such as `"24h"` timeframe values or Kubernetes UIDs) - not as DQL expressions. The interpolation lets a caller break out of string literals, append arbitrary DQL pipeline stages, and use `//` line comments (documented in the [Dynatrace DQL language reference](https://docs.dynatrace.com/docs/discover-dynatrace/platform/grail/dynatrace-query-language/dql-reference)) to discard the rest of the intended query.

The marginal-privilege ceiling is low because the operator's token also exposes `execute_dql` with full DQL access. What the injection grants is the ability to bypass the affected tools' contract: the `readOnlyHint: true` annotation that MCP clients may treat as a signal to auto-approve, the per-tool field selection (e.g., `| fields id, name, type`), the display caps (`maxProblemsToDisplay`, `maxVulnerabilitiesToDisplay`, `maxEntitiesToDisplay`), and the time-window bounds.

The vulnerable interpolations are:

| File | Line | Parameter | Interpolation |
|------|------|-----------|---------------|
| `src/capabilities/find-monitored-entity-by-name.ts` | 23 | `entityNames[]` | `` `fetch ${entityType} \| search "*${entityNames.join('*" OR "*')}*" \| fieldsAdd entity.type \| expand tags` `` |
| `src/capabilities/find-monitored-entity-by-name.ts` | 41 | `entityNames[]` | `` `smartscapeNodes "*" \| search "*${entityNames.join('*" OR "*')}*" \| fields id, name, type` `` |
| `src/capabilities/list-problems.ts` | 27 | `timeframe` | `` `fetch dt.davis.problems, from: now()-${timeframe}, to: now()` `` |
| `src/capabilities/list-vulnerabilities.ts` | 19 | `timeframe` | `` `fetch security.events, from: now()-${timeframe}, to: now()` `` |
| `src/capabilities/list-exceptions.ts` | 11 | `timeframe` | `` `fetch user.events, from: now()-${timeframe}, to: now()` `` |
| `src/capabilities/get-events-for-cluster.ts` | 20 | `timeframe` | `` `fetch events, from: now()-${timeframe}, to: now()` `` |
| `src/capabilities/get-events-for-cluster.ts` | 27 | `clusterId`, `kubernetesEntityId` | `` `\| filter k8s.cluster.uid == "${clusterId}" or dt.entity.kubernetes_cluster == "${kubernetesEntityId}"` `` |

All Zod schemas for these parameters use `z.string()` or `z.array(z.string())` with no pattern validation.

### PoC
**`clusterId` - quote-and-comment break-out.** With `clusterId = 'x" or 1==1 //'` the constructed query becomes:

```
| filter k8s.cluster.uid == "x" or 1==1 //" or dt.entity.kubernetes_cluster == ""
```

The first `"` closes the string literal, `or 1==1` neutralises the filter to match every row, and `//` discards the rest of the line including the `kubernetesEntityId` guard.

**`entityNames` - pipeline-stage injection.** With `entityNames = ['svc" | fields id, name, tags //']` the constructed smartscape query becomes:

```
smartscapeNodes "*" | search "*svc" | fields id, name, tags //*" | fields id, name, type
```

After the `//` line comment, the effective query is `smartscapeNodes "*" | search "*svc" | fields id, name, tags`. The original `| fields id, name, type` stage is suppressed and replaced with the attacker's field selection - the tool returns whatever field set the attacker requests (including ones not in the tool's documented output contract).

**`timeframe` - prefix injection.** With `timeframe = '30d, to: now() | fieldsAdd internal_secret //'` the list-problems query becomes:

```
fetch dt.davis.problems, from: now()-30d, to: now() | fieldsAdd internal_secret //, to: now()
| filter isNull(dt.davis.is_duplicate) OR not(dt.davis.is_duplicate)
...
```

A new pipeline stage is injected before the tool's intended `| filter`, and the rest of the query is commented out.

The server's own `verify_dql` tool can be used to confirm any specific injection payload parses as valid DQL.

### Impact
- A caller (typically via prompt injection of an LLM that has access to the affected tools) can bypass the tools' field-scope, time-window, and display caps.
- The affected tools are annotated `readOnlyHint: true`, which some MCP clients treat as a signal to auto-approve. The injection turns a "safe" read tool into an arbitrary-DQL surface.
- No new data access beyond what `execute_dql` already provides - the marginal impact is the auto-approval pathway and the broken tool contract, not privilege escalation.

## References
- https://github.com/dynatrace-oss/dynatrace-mcp/security/advisories/GHSA-pqh8-p93p-2rx7
- https://github.com/dynatrace-oss/dynatrace-mcp/pull/562
- https://github.com/dynatrace-oss/dynatrace-mcp/commit/15d3546c0618ffbaeaeca477337e08e92f2151bc
- https://github.com/dynatrace-oss/dynatrace-mcp
- https://github.com/dynatrace-oss/dynatrace-mcp/releases/tag/v2.1.1
