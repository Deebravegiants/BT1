# [H] CVE-2025-3909

## Summary
Severity: High
Advisory: CVE-2025-3909
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-3909
Type: osv

## Details
Thunderbird's handling of the X-Mozilla-External-Attachment-URL header can be exploited to execute JavaScript in the file:/// context. By crafting a nested email attachment (message/rfc822) and setting its content type to application/pdf, Thunderbird may incorrectly render it as HTML when opened, allowing the embedded JavaScript to run without requiring a file download. This behavior relies on Thunderbird auto-saving the attachment to /tmp and linking to it via the file:/// protocol, potentially enabling JavaScript execution as part of the HTML. This vulnerability affects Thunderbird < 128.10.1 and Thunderbird < 138.0.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2025-34/
- https://www.mozilla.org/security/advisories/mfsa2025-35/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1958376
