# [M] End-to-End encrypted file-drops can be made inaccessible

## Summary
Severity: Medium
Advisory: CVE-2023-35173
Aliases: GHSA-x7c7-v5r3-mg37
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-35173
Type: osv

## Details
Nextcloud End-to-end encryption app provides all the necessary APIs to implement End-to-End encryption on the client side. By providing an invalid meta data file, an attacker can make previously dropped files inaccessible. It is recommended that the Nextcloud End-to-end encryption app is upgraded to version 1.12.4 that contains the fix.

## References
- https://hackerone.com/reports/1914115
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35173.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-x7c7-v5r3-mg37
- https://nvd.nist.gov/vuln/detail/CVE-2023-35173
- https://github.com/nextcloud/end_to_end_encryption/pull/435
