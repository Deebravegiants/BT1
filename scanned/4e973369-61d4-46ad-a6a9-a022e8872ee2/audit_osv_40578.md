# [H] FreeScout Vulnerable to Unauthenticated Conversation Thread Injection via HMAC Length Bypass in FetchEmails

## Summary
Severity: High
Advisory: CVE-2026-53591
Aliases: GHSA-8vm3-wwq4-ggfx
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53591
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.223, an unauthenticated attacker can inject messages into any existing support conversation by sending a single email to the helpdesk's public address with a crafted `In-Reply-To` header. No credentials, tokens, or prior access are required. The injected message is rendered in the agent UI as a legitimate customer reply, the conversation is automatically reopened, and the `last_reply_from` field is set to the attacker's identity. Version 1.8.223 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53591.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-8vm3-wwq4-ggfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-53591
