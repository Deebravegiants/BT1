# [H] CVE-2020-10096

## Summary
Severity: High
Advisory: CVE-2020-10096
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10096
Type: osv

## Details
An issue was discovered in Zammad 3.0 through 3.2. It does not prevent caching of confidential data within browser memory. An attacker who either remotely compromises or obtains physical access to a user's workstation can browse the browser cache contents and obtain sensitive information. The attacker does not need to be authenticated with the application to view this information, as it would be available via the browser cache.

## References
- https://zammad.com/news/security-advisory-zaa-2020-11
