# [C] CVE-2021-32607

## Summary
Severity: Critical
Advisory: CVE-2021-32607
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-12
Source: https://osv.dev/vulnerability/CVE-2021-32607
Type: osv

## Details
An issue was discovered in Smartstore (aka SmartStoreNET) through 4.1.1. Views/PrivateMessages/View.cshtml does not call HtmlUtils.SanitizeHtml on a private message.

## References
- https://github.com/smartstore/SmartStoreNET/commit/5b4e60ae7124df0898975cb8f994f9f23db1fae3
- https://blog.sonarsource.com/smartstorenet-malicious-message-leading-to-e-commerce-takeover/
