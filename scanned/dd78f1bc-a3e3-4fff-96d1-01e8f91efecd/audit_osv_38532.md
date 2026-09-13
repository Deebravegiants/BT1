# [H] FreeScout Vulnerable to CSS Injection via Stored Style Tag in Mailbox Signature (CSRF Token Exfiltration)

## Summary
Severity: High
Advisory: CVE-2026-40497
Aliases: GHSA-fh99-wr77-pxq3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40497
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.213, FreeScout's `Helper::stripDangerousTags()` removes `<script>`, `<form>`, `<iframe>`, `<object>` but does NOT strip `<style>` tags. The mailbox signature field is saved via POST /mailbox/settings/{id} and later rendered unescaped via `{!! $conversation->getSignatureProcessed([], true) !!}` in conversation views. CSP allows `style-src * 'self' 'unsafe-inline'`, so injected inline styles execute freely. An attacker with access to mailbox settings (admin or agent with mailbox permission) can inject CSS attribute selectors to exfiltrate the CSRF token of any agent/admin who views a conversation in that mailbox. With the CSRF token, the attacker can perform any state-changing action as the victim (create admin accounts, change email/password, etc.) — privilege escalation from agent to admin. This is the result of an incomplete fix of GHSA-jqjf-f566-485j. That advisory reported XSS via mailbox signature. The fix applied `Helper::stripDangerousTags()` to the signature before saving. However, `stripDangerousTags()` only removes `script`, `form`, `iframe`, and `object` tags — it does NOT strip `<style>` tags, leaving CSS injection possible. Version 1.8.213 contains an updated fix.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40497.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-fh99-wr77-pxq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40497
- https://github.com/freescout-help-desk/freescout/commit/5aa8d633216f65995e80a7d4a921b784acc94df4
