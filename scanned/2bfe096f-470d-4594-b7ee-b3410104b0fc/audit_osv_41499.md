# [M] Wallos: SSRF via Test Email Notification - unvalidated SMTP host/port

## Summary
Severity: Medium
Advisory: CVE-2026-61638
Aliases: GHSA-f8r5-v75m-385h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-61638
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.6, POST /endpoints/notifications/testemailnotifications.php accepts smtpaddress and smtpport from POST body with zero SSRF validation. PHPMailer connects to attacker-supplied host:port. Every other notification endpoint uses ssrf_helper.php but email was missed. Any authenticated user can probe internal network, cloud metadata. This issue has been patched in version 4.9.6.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61638.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-f8r5-v75m-385h
- https://nvd.nist.gov/vuln/detail/CVE-2026-61638
- https://github.com/ellite/Wallos/commit/b75f13d0ffa3ed7e77e8e79e4b9fd3fc528c98d3
- https://github.com/ellite/Wallos/pull/1092
