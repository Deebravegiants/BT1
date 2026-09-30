# [C] Nodemailer before 8.0.3 SMTP Command Injection via envelope.size

## Summary
Severity: Critical
Advisory: CVE-2026-82854
Aliases: GHSA-c7w3-x93f-qmm8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82854
Type: osv

## Details
Nodemailer before 8.0.4 is vulnerable to SMTP command injection through the unsanitized envelope.size parameter. When an application passes a custom envelope object with a size property containing CRLF characters to sendMail(), the value is concatenated into the SMTP MAIL FROM command (as SIZE=...) without sanitization, allowing injection of arbitrary SMTP commands such as RCPT TO to silently add attacker-controlled recipients. Exploitation requires the application to expose the envelope size to attacker-controlled input, as Nodemailer does not include size in the default auto-constructed envelope.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82854.json
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-c7w3-x93f-qmm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-82854
- https://www.vulncheck.com/advisories/nodemailer-before-8.0.3-smtp-command-injection-via-envelope-size
