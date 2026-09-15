# [M] NocoDB: SSRF Protection Bypass in Notification Webhook Plugins (Slack, Discord, Mattermost, Teams)

## Summary
Severity: Medium
Advisory: GHSA-2c5x-4jgf-88mj
CVE: CVE-2026-46548
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-2c5x-4jgf-88mj
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary

The `request-filtering-agent` SSRF protection was non-functional in the four notification webhook plugins (Slack, Discord, Mattermost, Teams) because `httpAgent` / `httpsAgent` were passed as part of the request **body** rather than the axios **config**. An authenticated user with hook-creation permission could direct outbound POST requests to arbitrary internal hosts.

### Details

`axios.post(url, data, config)` expects connection agents in the third (config) argument. In all four plugins, the agents were placed in the second (data) argument and serialised as JSON body content:

```ts
// packages/nocodb/src/plugins/slack/Slack.ts (and Discord / Mattermost / Teams — identical pattern)
return await axios.post(webhook_url, {
  text,
  httpAgent: useAgent(webhook_url),   // wrong position — serialised, not used
  httpsAgent: useAgent(webhook_url),
});
```

The webhook flow: an Editor+ user creates a webhook with `notification.payload.channels[].webhook_url` pointing to an internal host; on trigger, `WebhookInvoker.invoke()` calls the plugin's `sendMessage()` which performs the outbound `axios.post` with no SSRF filtering applied.

This is distinct from GHSA-xr7v-j379-34v9, which covers a blind SSRF via HEAD in the upload-by-URL path.

### Impact

- Authenticated user (Editor+) can reach cloud-metadata endpoints (`169.254.169.254`) and internal services.
- Combined with verbose hook logging (`NC_AUTOMATION_LOG_LEVEL=ALL`), response bodies may be exfiltrated.

### Credit

This issue was reported by [@ik0z](https://github.com/ik0z).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-2c5x-4jgf-88mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-46548
- https://github.com/nocodb/nocodb
