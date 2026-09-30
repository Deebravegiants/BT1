# [M] Zitadel  allows User Enumeration by loginname attribute normalization

## Summary
Severity: Medium
Advisory: CVE-2025-31124
Aliases: GHSA-67m4-8g4w-633q
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-31124
Type: osv

## Details
Zitadel is open-source identity infrastructure software. ZITADEL administrators can enable a setting called "Ignoring unknown usernames" which helps mitigate attacks that try to guess/enumerate usernames. If enabled, ZITADEL will show the password prompt even if the user doesn't exist and report "Username or Password invalid". While the setting was correctly respected during the login flow, the user's username was normalized leading to a disclosure of the user's existence. This vulnerability is fixed in 2.71.6, 2.70.8, 2.69.9, 2.68.9, 2.67.13, 2.66.16, 2.65.7, 2.64.6, and 2.63.9.

## References
- https://github.com/zitadel/zitadel/releases/tag/v2.63.9
- https://github.com/zitadel/zitadel/releases/tag/v2.64.6
- https://github.com/zitadel/zitadel/releases/tag/v2.65.7
- https://github.com/zitadel/zitadel/releases/tag/v2.66.16
- https://github.com/zitadel/zitadel/releases/tag/v2.67.13
- https://github.com/zitadel/zitadel/releases/tag/v2.68.9
- https://github.com/zitadel/zitadel/releases/tag/v2.69.9
- https://github.com/zitadel/zitadel/releases/tag/v2.70.8
- https://github.com/zitadel/zitadel/releases/tag/v2.71.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31124.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-67m4-8g4w-633q
- https://nvd.nist.gov/vuln/detail/CVE-2025-31124
- https://github.com/zitadel/zitadel/commit/14de8ecac2afafee4975ed7ac26f3ca4a2b0f82c
