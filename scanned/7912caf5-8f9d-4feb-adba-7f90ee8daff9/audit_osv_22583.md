# [M] CVE-2022-32227

## Summary
Severity: Medium
Advisory: CVE-2022-32227
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32227
Type: osv

## Details
A cleartext transmission of sensitive information exists in Rocket.Chat <v5, <v4.8.2 and <v4.7.5 relating to Oauth tokens by having the permission "view-full-other-user-info", this could cause an oauth token leak in the product.

## References
- https://hackerone.com/reports/1517377
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32227.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32227
