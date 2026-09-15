# [M] Hi.Events before 1.11.1-beta Server-Side Request Forgery via Unvalidated Webhook Redirects

## Summary
Severity: Medium
Advisory: CVE-2026-76838
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76838
Type: osv

## Details
Hi.Events validates a webhook destination only when it is registered, never when it is used. NoInternalUrlRule in backend/app/Validators/Rules/NoInternalUrlRule.php resolves the hostname with gethostbyname() and rejects private and reserved ranges, which any public hostname passes. At dispatch, WebhookDispatchService takes the stored URL and calls it through spatie/laravel-webhook-server without repeating the check, and backend/config/webhook-server.php sets no Guzzle options, so redirect following remains enabled by default. A destination that answers with a redirect to a loopback, private or cloud metadata address therefore causes the server to issue that request, and changing the hostname's DNS record after registration reaches the same result because no resolution is repeated. The response is not discarded: WebhookResponseHandlerService stores the body on the webhook log and WebhookLogResource returns it from the webhook logs endpoint, so the requester reads what the internal service replied rather than inferring it. Both event and organizer webhooks share the rule and the dispatch path. Version 1.11.1-beta revalidates at dispatch, pins the validated address, checks every redirect hop, and decodes IPv6 transition addresses that previously bypassed the filter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76838.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76838
- https://www.vulncheck.com/advisories/hi-events-before-beta-server-side-request-forgery-via-unvalidated-webhook-redirects
- https://github.com/HiEventsDev/Hi.Events/commit/cfbf468bb5b1
- https://github.com/HiEventsDev/Hi.Events/pull/1311
- https://github.com/HiEventsDev/Hi.Events
- https://github.com/HiEventsDev/Hi.Events/blob/v.1.11.0-beta/backend/app/Validators/Rules/NoInternalUrlRule.php
