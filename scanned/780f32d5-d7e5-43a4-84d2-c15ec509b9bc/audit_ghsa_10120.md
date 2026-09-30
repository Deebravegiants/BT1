# [H] Novu has SSRF via conditions filter webhook bypasses validateUrlSsrf() protection

## Summary
Severity: High
Advisory: GHSA-4x48-cgf9-q33f
CWE: CWE-918
Ecosystem: npm
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-4x48-cgf9-q33f
Type: github-advisory

## Affected
- npm: `@novu/api` — affected >=0 <3.15.0

## Details
## Summary

The conditions filter webhook at `libs/application-generic/src/usecases/conditions-filter/conditions-filter.usecase.ts` line 261 sends POST requests to user-configured URLs using raw `axios.post()` with no SSRF validation. The HTTP Request workflow step in the same codebase correctly uses `validateUrlSsrf()` which blocks private IP ranges. The conditions webhook was not included in this protection.

## Root Cause

`conditions-filter.usecase.ts` line 261:
```typescript
return await axios.post(child.webhookUrl, payload, config).then((response) => {
  return response.data as Record<string, unknown>;
});
```

No call to `validateUrlSsrf()`. The `webhookUrl` comes from the workflow condition configuration with zero validation.

## Protected Code (for contrast)

`execute-http-request-step.usecase.ts` line 130:
```typescript
const ssrfValidationError = await validateUrlSsrf(url);
if (ssrfValidationError) {
  // blocked
}
```

This function resolves DNS and checks against private ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16). It exists in the codebase but is not applied to the conditions webhook path.

## Proof of Concept

1. Create a workflow with a condition step
2. Configure the condition's webhook URL to `http://169.254.169.254/latest/meta-data/iam/security-credentials/`
3. Trigger the workflow by sending a notification event
4. The worker evaluates the condition and calls `axios.post()` to the metadata endpoint
5. The response data is stored in execution details and accessible via the execution details API

## Impact

Full-read SSRF. The response body is returned as `Record<string, unknown>` for condition evaluation and stored in the execution details `raw` field. The `GET /execution-details` API returns this data.

The POST method limits some metadata endpoints (GCP requires GET, Azure requires GET), but AWS IMDSv1 accepts POST and returns credentials. Internal services accepting POST are also reachable.

## Suggested Fix

Extract `validateUrlSsrf()` to a shared utility and call it before the axios.post in conditions-filter.usecase.ts:

```typescript
const ssrfError = await validateUrlSsrf(child.webhookUrl);
if (ssrfError) {
  throw new Error('Webhook URL blocked by SSRF protection');
}
return await axios.post(child.webhookUrl, payload, config)...
```

## References
- https://github.com/novuhq/novu/security/advisories/GHSA-4x48-cgf9-q33f
- https://github.com/novuhq/novu/commit/87d965eb88340ac7cd262dd52c8015acd092dc68
- https://github.com/novuhq/novu
