# [M] CVE-2022-32219

## Summary
Severity: Medium
Advisory: CVE-2022-32219
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32219
Type: osv

## Details
An information disclosure vulnerability exists in Rocket.Chat <v4.7.5 which allowed the "users.list" REST endpoint gets a query parameter from JSON and runs Users.find(queryFromClientSide). This means virtually any authenticated user can access any data (except password hashes) of any user authenticated.

## References
- https://hackerone.com/reports/1140631
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32219.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32219
