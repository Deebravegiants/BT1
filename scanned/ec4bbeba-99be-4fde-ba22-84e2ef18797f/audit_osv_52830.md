# [M] CVE-2022-1520

## Summary
Severity: Medium
Advisory: CVE-2022-1520
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1520
Type: osv

## Details
When viewing an email message A, which contains an attached message B, where B is encrypted or digitally signed or both, Thunderbird may show an incorrect encryption or signature status. After opening and viewing the attached message B, when returning to the display of message A, the message A might be shown with the security status of message B. This vulnerability affects Thunderbird < 91.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1745019
