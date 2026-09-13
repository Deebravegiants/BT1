# [M] Wallos: Authenticated SSRF via per-user SMTP notification host (low-privilege user)

## Summary
Severity: Medium
Advisory: CVE-2026-77352
Aliases: GHSA-c75x-9vj6-57qj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-77352
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. From version 2.0.0 to before version 5.0.0, any authenticated Wallos user (no admin rights required) can make the server open arbitrary outbound SMTP connections to internal/link-local addresses, by setting the SMTP host of their personal email notifications to an internal IP. The per-user notification settings endpoint (endpoints/notifications/saveemailnotifications.php) performs no SSRF validation, and the notification cron (endpoints/cronjobs/sendnotifications.php) feeds that user-controlled host straight into PHPMailer ($mail->Host = $email['smtpAddress']). When the user's subscription notification fires, the server connects to the chosen host:port. This issue has been patched in version 5.0.0.

## References
- https://github.com/ellite/Wallos/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77352.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-c75x-9vj6-57qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-77352
- https://github.com/ellite/Wallos/commit/11eaf402e841a628c68a805694227ce66c45f6f3
