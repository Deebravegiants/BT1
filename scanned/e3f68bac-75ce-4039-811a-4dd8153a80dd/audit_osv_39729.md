# [H] FreeScout: Agent Impersonation via Missing HMAC Verification on Notification Reply Message-ID Path

## Summary
Severity: High
Advisory: CVE-2026-47123
Aliases: GHSA-6r38-6mcf-2ww3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-47123
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to 1.8.220, the email processing pipeline in FreeScout's FetchEmails command has two code paths for identifying agent (user) replies based on In-Reply-To / References headers. The notification reply path (notify-{thread_id}-{user_id}-...) extracts thread_id and user_id directly from the Message-ID without HMAC verification. An external attacker who can spoof the From address of a helpdesk agent can inject messages that FreeScout processes as legitimate agent replies — which are then automatically forwarded to customers via the legitimate SMTP server. This vulnerability is fixed in 1.8.220.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47123.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-6r38-6mcf-2ww3
- https://nvd.nist.gov/vuln/detail/CVE-2026-47123
- https://github.com/freescout-help-desk/freescout/commit/d902f19038213c6a376947d269b00440908e88a0
- https://vincent.vulcoord.net/score/?state=Not+Scored&year=2026&year=2025&assigned_to=a165dae3-480e-4f7d-bbb8-9b1d78115b69&cve=CVE-2026-47123&analyze=1
