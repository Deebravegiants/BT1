# [M] Command Injection in Appointment Emails for Nextcloud Calendar

## Summary
Severity: Medium
Advisory: CVE-2022-24838
Aliases: GHSA-8xv5-4855-24qf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-24838
Type: osv

## Details
Nextcloud Calendar is a calendar application for the nextcloud framework. SMTP Command Injection in Appointment Emails via Newlines: as newlines and special characters are not sanitized in the email value in the JSON request, a malicious attacker can inject newlines to break out of the `RCPT TO:<BOOKING USER'S EMAIL> ` SMTP command and begin injecting arbitrary SMTP commands. It is recommended that Calendar is upgraded to 3.2.2. There are no workaround available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24838.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8xv5-4855-24qf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24838
- https://github.com/nextcloud/calendar/commit/7b70edfb8a0fcf0926f613ababcbd56c6ecd9f35
- https://github.com/nextcloud/calendar/pull/4073
