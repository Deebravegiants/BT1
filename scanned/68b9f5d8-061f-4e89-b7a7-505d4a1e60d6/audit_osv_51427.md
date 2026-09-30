# [H] CVE-2021-30552

## Summary
Severity: High
Advisory: CVE-2021-30552
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-15
Source: https://osv.dev/vulnerability/CVE-2021-30552
Type: osv

## Details
Use after free in Extensions in Google Chrome prior to 91.0.4472.101 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ETMZL6IHCTCTREEL434BQ4THQ7EOHJ43/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAT6EOXVQFE6JFMFQF4IKAOUQSHMHL54/
- https://security.gentoo.org/glsa/202107-06
- https://chromereleases.googleblog.com/2021/06/stable-channel-update-for-desktop.html
- https://crbug.com/1200679
