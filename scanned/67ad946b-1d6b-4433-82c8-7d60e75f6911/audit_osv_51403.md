# [H] CVE-2021-30528

## Summary
Severity: High
Advisory: CVE-2021-30528
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2021-30528
Type: osv

## Details
Use after free in WebAuthentication in Google Chrome on Android prior to 91.0.4472.77 allowed a remote attacker who had compromised the renderer process of a user who had saved a credit card in their Google account to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ETMZL6IHCTCTREEL434BQ4THQ7EOHJ43/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAT6EOXVQFE6JFMFQF4IKAOUQSHMHL54/
- http://packetstormsecurity.com/files/172844/Chrome-Sandbox-Escape.html
- https://chromereleases.googleblog.com/2021/05/stable-channel-update-for-desktop_25.html
- https://security.gentoo.org/glsa/202107-06
- https://crbug.com/1206329
