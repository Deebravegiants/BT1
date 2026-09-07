# [H] Budibase: SSRF in Automation Steps - Webhook, Zapier, N8N, Slack, Discord Bypass IP Blacklist

## Summary
Severity: High
Advisory: GHSA-5fpj-28rv-84r7
CVE: CVE-2026-35219
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-5fpj-28rv-84r7
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.41.3

## Details
## Summary

Budibase automation steps (outgoing webhook, Zapier, n8n, Slack, Discord, Make.com) make server-side HTTP requests to user-provided URLs using `node-fetch` directly, completely bypassing the IP blacklist protection that exists in the REST API integration. Additionally, the REST API blacklist itself defaults to empty when `BLACKLIST_IPS` is not configured.

## Vulnerable Code

### Automation Steps (No Blacklist)

All automation steps use `fetch()` directly without any IP validation:

**`packages/server/src/automations/steps/outgoingWebhook.ts` line 69:**
```typescript
const response = await fetch(url, request)  // No blacklist check
```

**`packages/server/src/automations/steps/zapier.ts` line 34:**
```typescript
response = await fetch(url, {method: "post", ...})  // No blacklist check
```

**`packages/server/src/automations/steps/n8n.ts` line 53:**
```typescript
response = await fetch(url, request)  // No blacklist check
```

**`packages/server/src/automations/steps/slack.ts` line 20:**
```typescript
response = await fetch(url, {method: "post", ...})  // No blacklist check
```

**`packages/server/src/automations/steps/discord.ts` line 29:**
```typescript
response = await fetch(url, {method: "post", ...})  // No blacklist check
```

### REST API Integration (Empty Default Blacklist)

**`packages/server/src/integrations/rest.ts` line 684:**
```typescript
if (await blacklist.isBlacklisted(url)) {
  throw new Error("Cannot connect to URL.")
}
```

But `BLACKLIST_IPS` env var defaults to undefined, so the blacklist is empty:

**`packages/backend-core/src/blacklist/blacklist.ts` lines 39-45:**
```typescript
if (blackListArray?.length === 0) {
  return false  // Always passes when no IPs configured
}
```

## Impact

- **Automation steps**: ANY user can create automations with webhook/Zapier/n8n/Slack/Discord steps pointing to internal IPs. These completely bypass the blacklist module
- **REST API**: Even when BLACKLIST_IPS is configured, it only blocks listed IPs. Default deployments have no protection.
- **Cloud metadata**: `http://169.254.169.254/latest/meta-data/` accessible via any automation step
- **Internal services**: Access databases, admin panels, Kubernetes API on private IPs

## Remediation

1. Apply blacklist checks to ALL outbound HTTP requests, including automation steps
2. Add hardcoded default private IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16)
3. Use a centralized HTTP client wrapper instead of direct `fetch()` calls
4. SSRF protection should be on by default, not opt-in via environment variable

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-5fpj-28rv-84r7
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.41.3
