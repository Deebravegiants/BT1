# [H] mailcow: dockerized vulnerable to password reset poisoning

## Summary
Severity: High
Advisory: CVE-2025-25198
Aliases: GHSA-3mvx-qw4r-fcqf
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-25198
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. Prior to version 2025-01a, a vulnerability in mailcow's password reset functionality allows an attacker to manipulate the `Host HTTP` header to generate a password reset link pointing to an attacker-controlled domain. This can lead to account takeover if a user clicks the poisoned link. Version 2025-01a contains a patch. As a workaround, deactivate the password reset functionality by clearing `Notification email sender` and `Notification email subject` under System -> Configuration -> Options -> Password Settings.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25198.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-3mvx-qw4r-fcqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-25198
