# [M] Ownership check missing when updating or deleting mail attachments in Nextcloud mail

## Summary
Severity: Medium
Advisory: CVE-2022-31131
Aliases: GHSA-xhv7-5mhv-299j
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2022-31131
Type: osv

## Details
Nextcloud mail is a Mail app for the Nextcloud home server product. Versions of Nextcloud mail prior to 1.12.2 were found to be missing user account ownership checks when performing tasks related to mail attachments. Attachments may have been exposed to incorrect system users. It is recommended that the Nextcloud Mail app is upgraded to 1.12.2. There are no known workarounds for this issue. ### Workarounds No workaround available ### References * [Pull request](https://github.com/nextcloud/mail/pull/6600) * [HackerOne](https://hackerone.com/reports/1579820) ### For more information If you have any questions or comments about this advisory: * Create a post in [nextcloud/security-advisories](https://github.com/nextcloud/security-advisories/discussions) * Customers: Open a support ticket at [support.nextcloud.com](https://support.nextcloud.com)

## References
- https://github.com/nextcloud/mail/pull/6600/commits/6dd2527be8d4f6788b449c8a8f5577628b990605
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31131.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-xhv7-5mhv-299j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31131
- https://github.com/nextcloud/mail/pull/6600
