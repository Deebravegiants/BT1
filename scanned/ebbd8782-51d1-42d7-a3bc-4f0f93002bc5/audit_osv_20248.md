# [C] CVE-2021-32608

## Summary
Severity: Critical
Advisory: CVE-2021-32608
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-12
Source: https://osv.dev/vulnerability/CVE-2021-32608
Type: osv

## Details
An issue was discovered in Smartstore (aka SmartStoreNET) through 4.1.1. Views/Boards/Partials/_ForumPost.cshtml does not call HtmlUtils.SanitizeHtml on certain text for a forum post.

## References
- https://github.com/smartstore/SmartStoreNET/commit/ae03d45e23734555a2aef0b0c3d33c21e076c20f
- https://blog.sonarsource.com/smartstorenet-malicious-message-leading-to-e-commerce-takeover/
