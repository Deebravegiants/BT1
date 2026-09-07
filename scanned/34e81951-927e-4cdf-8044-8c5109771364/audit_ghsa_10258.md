# [M] NocoBase has SSRF in Workflow HTTP Request and Custom Request Plugins

## Summary
Severity: Medium
Advisory: GHSA-mvvv-v22x-xqwp
CVE: CVE-2026-40346
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-mvvv-v22x-xqwp
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-workflow-request` — affected >=0 <2.0.37

## Details
## Summary

NocoBase's workflow HTTP request plugin and custom request action plugin make server-side HTTP requests to user-provided URLs without any SSRF protection. An authenticated user can access internal network services, cloud metadata endpoints, and localhost.

## Vulnerable Code

### 1. Workflow HTTP Request Plugin

**`packages/plugins/@nocobase/plugin-workflow-request/src/server/RequestInstruction.ts` lines 117-128:**
```typescript
return axios.request({
  url: trim(url),  // User-controlled, no validation
  method,
  headers,
  params,
  timeout,
  ...(method.toLowerCase() !== 'get' && data != null
    ? { data: transformer ? await transformer(data) : data }
    : {}),
});
```

The `url` at line 98 comes directly from user workflow configuration with only whitespace trimming.

### 2. Custom Request Action Plugin

**`packages/plugins/@nocobase/plugin-action-custom-request/src/server/actions/send.ts` lines 172-198:**
```typescript
const axiosRequestConfig = {
  baseURL: ctx.origin,
  ...options,
  url: getParsedValue(url, variables),  // User-controlled via template
  headers: { ... },
  params: getParsedValue(arrayToObject(params), variables),
  data: getParsedValue(toJSON(data), variables),
};
const res = await axios(axiosRequestConfig);  // No IP validation
```

## Missing Protections

- No `request-filtering-agent` or SSRF library (confirmed via grep across entire codebase)
- No private IP range filtering
- No cloud metadata endpoint blocking
- No URL scheme validation
- No DNS rebinding protection

## Attack Scenario

1. Authenticated user creates a workflow with HTTP Request node
2. Sets URL to `http://169.254.169.254/latest/meta-data/iam/security-credentials/`
3. Triggers the workflow
4. Server fetches AWS metadata and returns IAM credentials in workflow execution logs

Alternatively via Custom Request action:
1. Create custom request with URL `http://127.0.0.1:5432` or `http://10.0.0.1:8080/admin`
2. Execute the action
3. Server makes request to internal service

## Impact

- **Cloud metadata theft**: AWS/GCP/Azure credentials via metadata endpoints
- **Internal network access**: Scan and interact with services on private IP ranges
- **Database access**: Connect to localhost databases (PostgreSQL, Redis, etc.)
- **Authentication required**: Yes (authenticated user), but any workspace member can create workflows

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-mvvv-v22x-xqwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40346
- https://github.com/nocobase/nocobase/pull/9079
- https://github.com/nocobase/nocobase/commit/2853368243ed07339c62c548b7d475f4eeaada59
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.37
