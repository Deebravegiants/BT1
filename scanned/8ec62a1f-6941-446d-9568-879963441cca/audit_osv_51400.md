# [H] CVE-2021-30525

## Summary
Severity: High
Advisory: CVE-2021-30525
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2021-30525
Type: osv

## Details
Use after free in TabGroups in Google Chrome prior to 91.0.4472.77 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ETMZL6IHCTCTREEL434BQ4THQ7EOHJ43/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAT6EOXVQFE6JFMFQF4IKAOUQSHMHL54/
- https://chromereleases.googleblog.com/2021/05/stable-channel-update-for-desktop_25.html
- https://security.gentoo.org/glsa/202107-06
- https://crbug.com/1197888
