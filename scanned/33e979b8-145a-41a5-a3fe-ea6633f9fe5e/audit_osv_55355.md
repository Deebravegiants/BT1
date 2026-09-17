# [M] CVE-2025-3523

## Summary
Severity: Medium
Advisory: CVE-2025-3523
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-3523
Type: osv

## Details
When an email contains multiple attachments with external links via the X-Mozilla-External-Attachment-URL header, only the last link is shown when hovering over any attachment. Although the correct link is used on click, the misleading hover text could trick users into downloading content from untrusted sources. This vulnerability affects Thunderbird < 137.0.2 and Thunderbird < 128.9.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-26/
- https://www.mozilla.org/security/advisories/mfsa2025-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1958385
