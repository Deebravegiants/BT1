# [M] Uptime Kuma Server-side Template Injection (SSTI) in Notification Templates Allows Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-vffh-c9pq-4crh
CWE: CWE-1336, CWE-36
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-vffh-c9pq-4crh
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected 2.0.0-dev.0

## Details
### Summary

In some Notification types (e.g., Webhook, Telegram), the `send()` function allows user-controlled renderTemplate input. This leads to a Server-side Template Injection (SSTI) vulnerability that can be exploited to read arbitrary files from the server.



### Details

The root cause is how Uptime Kuma renders user-controlled templates via `renderTemplate()`. The function instantiates a Liquid template engine and parses the `template` argument without sanitization:

```js
async renderTemplate(template, msg, monitorJSON, heartbeatJSON) {
    const engine = new Liquid();
    const parsedTpl = engine.parse(template);

    // ...
}
```

In some Notification flows, the `send()` implementation passes user-editable fields directly into `renderTemplate()`:
```js
// webhook.js
if (notification.webhookContentType === "form-data") {
    const formData = new FormData();
    formData.append("data", JSON.stringify(data));
    config.headers = formData.getHeaders();
    data = formData;
} else if (notification.webhookContentType === "custom") {
    data = await this.renderTemplate(notification.webhookCustomBody, msg, monitorJSON, heartbeatJSON); //<- this line cause SSTI
}
```

Because `notification` can be edited by users and is rendered by the Liquid engine without proper sandboxing or a whitelist of allowed operations, an attacker can supply a crafted template that causes the server to read arbitrary files. In particular, Liquid’s template tags (e.g. `{% render ... %}`) can be abused to include server-side files if the engine is not restricted, resulting in Server-side Template Injection (SSTI) that leaks sensitive file contents.



### PoC

1. Open Uptime Kuma → **Notifications** → **Add** or **Edit** an existing Webhook notification.
2. Set notification type to **Webhook** and set **Request Body**  to **Custom Body**.
3. Paste the following JSON into the custom request body:

```json
{
  "Title": {% render '/etc/passwd' %}
}
```

4. Click test.
5. Your webhook will receive the file content



### Impact

This is a post-authentication Server-side Template Injection (SSTI) vulnerability that allows an authenticated user to perform arbitrary file read on the server.

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-vffh-c9pq-4crh
- https://github.com/louislam/uptime-kuma
