# [H] CVE-2025-32354

## Summary
Severity: High
Advisory: CVE-2025-32354
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-32354
Type: osv

## Details
In Zimbra Collaboration (ZCS) 9.0 through 10.1, a Cross-Site Request Forgery (CSRF) vulnerability exists in the GraphQL endpoint (/service/extension/graphql) of Zimbra webmail due to a lack of CSRF token validation. This allows attackers to perform unauthorized GraphQL operations, such as modifying contacts, changing account settings, and accessing sensitive user data when an authenticated user visits a malicious website.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.4#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32354.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32354
