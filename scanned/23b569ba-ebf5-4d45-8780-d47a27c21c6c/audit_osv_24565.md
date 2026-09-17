# [C] CVE-2023-22894

## Summary
Severity: Critical
Advisory: CVE-2023-22894
Aliases: GHSA-jjqf-j4w7-92w8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-22894
Type: osv

## Details
Strapi through 4.5.5 allows attackers (with access to the admin panel) to discover sensitive user details by exploiting the query filter. The attacker can filter users by columns that contain sensitive information and infer a value from API responses. If the attacker has super admin access, then this can be exploited to discover the password hash and password reset token of all users. If the attacker has admin panel access to an account with permission to access the username and email of API users with a lower privileged role (e.g., Editor or Author), then this can be exploited to discover sensitive information for all API users but not other admin accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22894.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22894
- https://github.com/strapi/strapi/releases
- https://strapi.io/blog/security-disclosure-of-vulnerabilities-cve
- https://www.ghostccamm.com/blog/multi_strapi_vulns/
