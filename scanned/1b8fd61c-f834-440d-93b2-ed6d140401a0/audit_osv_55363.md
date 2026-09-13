# [M] CVE-2025-3932

## Summary
Severity: Medium
Advisory: CVE-2025-3932
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-3932
Type: osv

## Details
It was possible to craft an email that showed a tracking link as an attachment. If the user attempted to open the attachment, Thunderbird automatically accessed the link. The configuration to block remote content did not prevent that. Thunderbird has been fixed to no longer allow access to web pages listed in the X-Mozilla-External-Attachment-URL header of an email. This vulnerability affects Thunderbird < 128.10.1 and Thunderbird < 138.0.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2025-34/
- https://www.mozilla.org/security/advisories/mfsa2025-35/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1960412
