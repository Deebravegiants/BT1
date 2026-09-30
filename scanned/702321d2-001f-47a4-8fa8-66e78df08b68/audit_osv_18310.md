# [C] CVE-2020-26030

## Summary
Severity: Critical
Advisory: CVE-2020-26030
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-26030
Type: osv

## Details
An issue was discovered in Zammad before 3.4.1. There is an authentication bypass in the SSO endpoint via a crafted header, when SSO is not configured. An attacker can create a valid and authenticated session that can be used to perform any actions in the name of other users.

## References
- https://zammad.com/news/security-advisory-zaa-2020-18
