# [H] FreeScout Stored XSS vulnerability in mailbox auto-reply: payload reaches every customer's email client (no CSP), bypassing strip_tags validator with mixed text+HTML content

## Summary
Severity: High
Advisory: CVE-2026-41904
Aliases: GHSA-q3fh-rj9h-jfrc
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41904
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.217, a user with updateAutoReply permission can store an XSS payload in the mailbox auto-reply message. The payload is rendered unescaped in the auto-reply email sent to every customer who contacts the mailbox. Email clients do not enforce CSP, so the payload executes in the customer's webmail / mail-client context. This issue has been patched in version 1.8.217.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41904.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-q3fh-rj9h-jfrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-41904
