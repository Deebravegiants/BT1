# [M] Inviting excessive long email addresses to a calendar event makes the Nextcloud server unresponsive

## Summary
Severity: Medium
Advisory: CVE-2023-45150
Aliases: GHSA-r936-8gwm-w452
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-45150
Type: osv

## Details
Nextcloud calendar is a calendar app for the Nextcloud server platform. Due to missing precondition checks the server was trying to validate strings of any length as email addresses even when megabytes of data were provided, eventually making the server busy and unresponsive. It is recommended that the Nextcloud Calendar app is upgraded to 4.4.4. The only workaround for users unable to upgrade is to disable the calendar app.

## References
- https://hackerone.com/reports/2058337
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45150.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-r936-8gwm-w452
- https://nvd.nist.gov/vuln/detail/CVE-2023-45150
- https://github.com/nextcloud/calendar/pull/5358
