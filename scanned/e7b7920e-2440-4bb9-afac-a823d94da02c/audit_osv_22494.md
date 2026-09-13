# [M] SMTP Command Injection in iCalendar Attachments to emails via newlines in Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2022-31014
Aliases: GHSA-264h-3v4w-6xh2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/CVE-2022-31014
Type: osv

## Details
Nextcloud server is an open source personal cloud server. Affected versions were found to be vulnerable to SMTP command injection. The impact varies based on which commands are supported by the backend SMTP server. However, the main risk here is that the attacker can then hijack an already-authenticated SMTP session and run arbitrary SMTP commands as the email user, such as sending emails to other users, changing the FROM user, and so on. As before, this depends on the configuration of the server itself, but newlines should be sanitized to mitigate such arbitrary SMTP command injection. It is recommended that the Nextcloud Server is upgraded to 22.2.8 , 23.0.5 or 24.0.1. There are no known workarounds for this issue.

## References
- https://hackerone.com/reports/1516377
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31014.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-264h-3v4w-6xh2
- https://nvd.nist.gov/vuln/detail/CVE-2022-31014
- https://github.com/nextcloud/server/pull/32428
