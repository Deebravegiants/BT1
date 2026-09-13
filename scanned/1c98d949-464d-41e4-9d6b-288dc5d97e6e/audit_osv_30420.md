# [M] Nextcloud Server allows users to copy folder that contain files that are blocked by the files access control

## Summary
Severity: Medium
Advisory: CVE-2024-52514
Aliases: GHSA-g8pr-g25r-58xj
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52514
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. After a user received a share with some files inside being blocked by the files access control, the user would still be able to copy the intermediate folder inside Nextcloud allowing them to afterwards potentially access the blocked files depending on the user access control rules. It is recommended that the Nextcloud Server is upgraded to 27.1.9, 28.0.5 or 29.0.0 and Nextcloud Enterprise Server is upgraded to 21.0.9.18, 22.2.10.23, 23.0.12.18, 24.0.12.14, 25.0.13.9, 26.0.13.3, 27.1.9, 28.0.5 or 29.0.0.

## References
- https://hackerone.com/reports/2447316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52514.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-g8pr-g25r-58xj
- https://nvd.nist.gov/vuln/detail/CVE-2024-52514
- https://github.com/nextcloud/server/commit/5fffbcfe8650eab75b00e8d188fbc95b0e43f3a8
- https://github.com/nextcloud/server/pull/44889
