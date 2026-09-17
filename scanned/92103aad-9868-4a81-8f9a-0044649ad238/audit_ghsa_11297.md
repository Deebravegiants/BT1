# [H] Postiz has Multiple SSRF Vectors - Webhooks, RSS Feed, URL Loader

## Summary
Severity: High
Advisory: GHSA-89v5-38xr-9m4j
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-89v5-38xr-9m4j
Type: github-advisory

## Affected
- npm: `postiz` — affected >=0

## Details
## Summary

Postiz has multiple SSRF vulnerabilities where user-provided URLs are fetched server-side without any IP validation or SSRF protection.

## Vulnerable Code

### 1. Webhook Send Endpoint (Most Critical)

**`apps/backend/src/api/routes/webhooks.controller.ts` lines 58-70:**
```typescript
async sendWebhook(@Body() body: any, @Query('url') url: string) {
  try {
    await fetch(url, {  // No URL validation
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) { }
  return { send: true };
}
```

Accepts arbitrary URL via query parameter and fetches directly.

### 2. Stored Webhook Delivery

**`apps/orchestrator/src/activities/post.activity.ts` lines 256-281:**
```typescript
async sendWebhooks(postId: string, orgId: string, integrationId: string) {
  const webhooks = await this._webhookService.getWebhooks(orgId);
  return Promise.all(
    webhooks.map(async (webhook) => {
      await fetch(webhook.url, {  // Stored URL, no validation
        method: 'POST',
        body: JSON.stringify(post),
      });
    })
  );
}
```

### 3. RSS/XML Feed Parser

**`libraries/nestjs-libraries/src/database/prisma/autopost/autopost.service.ts` line 135:**
```typescript
async loadXML(url: string) {
  const { items } = await parser.parseURL(url);  // No URL validation
}
```

### 4. HTML Content Loader

**`libraries/nestjs-libraries/src/database/prisma/autopost/autopost.service.ts` line 185:**
```typescript
async loadUrl(url: string) {
  const loadDom = new JSDOM(await (await fetch(url)).text());  // No validation
}
```

## Missing Protections

- No `request-filtering-agent` or SSRF library
- No private IP range filtering
- No cloud metadata endpoint blocking
- No DNS rebinding protection
- URL validation only via `@IsUrl()` decorator (format only, no IP check)

## Attack Scenarios

1. `POST /webhooks/send?url=http://169.254.169.254/latest/meta-data/` → AWS metadata theft
2. `POST /autopost/send?url=http://127.0.0.1:6379` → Internal Redis access
3. Create webhook with `http://10.0.0.1:8080/admin` → Internal service access on post publish

## Impact

- **Cloud metadata theft**: AWS/GCP/Azure credentials
- **Internal network scanning**: Full access to private IP ranges
- **Multiple entry points**: Webhooks, RSS feeds, URL loader all vulnerable

## References
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-89v5-38xr-9m4j
- https://github.com/gitroomhq/postiz-app/commit/0ad89ccd26b1c387c4f3f3544b18c20d33586466
- https://github.com/gitroomhq/postiz-app/commit/be5d871896e97cb1f5a2c9241f156b6a1e1debe8
- https://github.com/gitroomhq/postiz-app
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.2
