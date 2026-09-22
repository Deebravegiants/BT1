# [M] Netmaker through 1.6.0 Improper Certificate Validation in SMTP Client

## Summary
Severity: Medium
Advisory: CVE-2026-81034
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81034
Type: osv

## Details
Netmaker disables certificate verification on the connection to the configured mail server. The sender in pro/email/smtp.go assigns a TLS configuration whose skip-verify field is set to true unconditionally, directly beneath a comment stating that the setting should be false in production. No configuration value governs it and no code path restores verification, so the client accepts any certificate the mail server presents, including one an interposing party supplies. Mail that Netmaker sends over that connection includes password-reset messages carrying single-use tokens and user invitations carrying enrolment links, so a party positioned on the path between the server and its mail relay can read those messages in transit and use a captured reset token before the intended recipient does. The setting is absent from the development branch but present in the latest release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81034
- https://www.vulncheck.com/advisories/netmaker-through-1.6.0-improper-certificate-validation-in-smtp-client
- https://github.com/gravitl/netmaker/issues/4062
- https://github.com/gravitl/netmaker
- https://github.com/gravitl/netmaker/blob/v1.6.0/pro/email/smtp.go
