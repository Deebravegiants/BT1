# [M] CVE-2018-7563

## Summary
Severity: Medium
Advisory: CVE-2018-7563
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2018-7563
Type: osv

## Details
An issue was discovered in GLPI through 9.2.1. The application is affected by XSS in the query string to front/preference.php. An attacker is able to create a malicious URL that, if opened by an authenticated user with debug privilege, will execute JavaScript code supplied by the attacker. The attacker-supplied code can perform a wide variety of actions, such as stealing the victim's session token or login credentials, performing arbitrary actions on the victim's behalf, and logging their keystrokes.

## References
- https://github.com/glpi-project/glpi/pull/3647
- https://membership.backbox.org/glpi-9-2-1-multiple-vulnerabilities/
