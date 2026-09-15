# [M] Mobile password gets saved in dictionary under conditions

## Summary
Severity: Medium
Advisory: CVE-2024-45833
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-09-16
Source: https://osv.dev/vulnerability/CVE-2024-45833
Type: osv

## Details
Mattermost Mobile Apps versions <=2.18.0 fail to disable autocomplete during login while typing the password and visible password is selected, which allows the password to get saved in the dictionary when the user has Swiftkey as the default keyboard, the masking is off and the password contains a special character..

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45833.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45833
