# [C] CVE-2024-55560

## Summary
Severity: Critical
Advisory: CVE-2024-55560
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-08
Source: https://osv.dev/vulnerability/CVE-2024-55560
Type: osv

## Details
MailCleaner before 28d913e has default values of ssh_host_dsa_key, ssh_host_rsa_key, and ssh_host_ed25519_key that persist after installation.

## References
- https://github.com/MailCleaner/MailCleaner/wiki/Watchdogs#host_keys
- https://www.mailcleaner.net/infobox/mc-info-box.php
- https://github.com/MailCleaner/MailCleaner/commit/28d913eaa044b689eb114f72ebe92d48cb4aaca7
