# [M] CVE-2018-17883

## Summary
Severity: Medium
Advisory: CVE-2018-17883
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2018-17883
Type: osv

## Details
An issue was discovered in Open Ticket Request System (OTRS) 6.0.x before 6.0.12. An attacker could send an e-mail message with a malicious link to an OTRS system or an agent. If a logged-in agent opens this link, it could cause the execution of JavaScript in the context of OTRS.

## References
- https://community.otrs.com/category/release-and-security-notes-en/
- https://community.otrs.com/security-advisory-2018-06-security-update-for-otrs-framework/
