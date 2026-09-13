# [M] Users can set up workflows using restricted and invisible system tags in Nextcloud

## Summary
Severity: Medium
Advisory: CVE-2023-30539
Aliases: GHSA-3m2f-v8x7-9w99
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2023-04-17
Source: https://osv.dev/vulnerability/CVE-2023-30539
Type: osv

## Details
Nextcloud is a personal home server system. Depending on the set up tags and other workflows this issue can be used to limit access of others or being able to grant them access when there are system tag based files access control or files retention rules. It is recommended that the Nextcloud Server is upgraded to 24.0.11 or 25.0.5, the Nextcloud Enterprise Server to 21.0.9.11, 22.2.10.11, 23.0.12.6, 24.0.11 or 25.0.5, and the Nextcloud Files automated tagging app to 1.11.1, 1.12.1, 1.13.1, 1.14.2, 1.15.3 or 1.16.1. Users unable to upgrade should disable all workflow related apps. Users are advised to upgrade.

## References
- https://hackerone.com/reports/1895976
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30539.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-3m2f-v8x7-9w99
- https://nvd.nist.gov/vuln/detail/CVE-2023-30539
- https://github.com/nextcloud/files_automatedtagging/pull/705
- https://github.com/nextcloud/server/pull/37252
