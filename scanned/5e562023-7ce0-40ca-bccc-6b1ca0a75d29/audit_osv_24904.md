# [M] CVE-2023-28325

## Summary
Severity: Medium
Advisory: CVE-2023-28325
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-05-11
Source: https://osv.dev/vulnerability/CVE-2023-28325
Type: osv

## Details
An improper authorization vulnerability exists in Rocket.Chat <6.0 that could allow a hacker to manipulate the rid parameter and change the updateMessage method that only checks whether the user is allowed to edit message in the target room.

## References
- https://hackerone.com/reports/1406479
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28325.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28325
