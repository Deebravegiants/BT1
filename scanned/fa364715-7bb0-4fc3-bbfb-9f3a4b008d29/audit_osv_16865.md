# [M] CVE-2020-10100

## Summary
Severity: Medium
Advisory: CVE-2020-10100
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10100
Type: osv

## Details
An issue was discovered in Zammad 3.0 through 3.2. It allows for users to view ticket customer details associated with specific customers. However, the application does not properly implement access controls related to this functionality. As such, users of one company are able to access ticket data from other companies. Due to the multi-tenant nature of this application, users who can access ticket details from one organization to the next allows for users to exfiltrate potentially sensitive data of other companies.

## References
- https://zammad.com/news/security-advisory-zaa-2020-05
