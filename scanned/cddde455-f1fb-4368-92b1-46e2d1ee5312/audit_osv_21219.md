# [M] CVE-2021-41179

## Summary
Severity: Medium
Advisory: CVE-2021-41179
Aliases: GHSA-7hvh-rc6f-px23
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-41179
Type: osv

## Details
Nextcloud is an open-source, self-hosted productivity platform. Prior to Nextcloud Server versions 20.0.13, 21.0.5, and 22.2.0, the Two-Factor Authentication wasn't enforced for pages marked as public. Any page marked as `@PublicPage` could thus be accessed with a valid user session that isn't authenticated. This particularly affects the Nextcloud Talk application, as this could be leveraged to gain access to any private chat channel without going through the Two-Factor flow. It is recommended that the Nextcloud Server be upgraded to 20.0.13, 21.0.5 or 22.2.0. There are no known workarounds aside from upgrading.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-7hvh-rc6f-px23
- https://hackerone.com/reports/1322865
- https://github.com/nextcloud/server/pull/28725
