# [H] FreeScout: Improper Authorization in Phone Conversation Creation Enables Cross-Mailbox Hidden Customer Modification

## Summary
Severity: High
Advisory: CVE-2026-40591
Aliases: GHSA-9ff4-mmhv-x6jp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40591
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.214, the phone-conversation creation flow accepts attacker-controlled `customer_id`, `name`, `to_email`, and `phone` values and resolves the target customer in the backend without enforcing mailbox-scoped customer visibility. As a result, a low-privileged agent who can create a phone conversation in Mailbox A can bind the new Mailbox A phone conversation to a hidden customer from Mailbox B and add a new alias email to that hidden customer record by supplying `to_email`. Version 1.8.214 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40591.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-9ff4-mmhv-x6jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40591
- https://github.com/freescout-help-desk/freescout/commit/83eea1ca47d97c6cdc90c501734bc2579b014a34
