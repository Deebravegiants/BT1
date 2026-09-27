# [H] CVE-2022-2617

## Summary
Severity: High
Advisory: CVE-2022-2617
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-12
Source: https://osv.dev/vulnerability/CVE-2022-2617
Type: osv

## Details
Use after free in Extensions API in Google Chrome prior to 104.0.5112.79 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via specific UI interactions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4NMJURTG5RO3TGD7ZMIQ6Z4ZZ3SAVYE/
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202208-35
- https://crbug.com/1292451
