# [C] CVE-2021-21150

## Summary
Severity: Critical
Advisory: CVE-2021-21150
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/CVE-2021-21150
Type: osv

## Details
Use after free in Downloads in Google Chrome on Windows prior to 88.0.4324.182 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BI6ZIJQYP5DFMYVX4J5OGOU2NQLEZ3SB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FE5SIKEVYTMDCC5OSXGOM2KRPYLHYMQX/
- https://chromereleases.googleblog.com/2021/02/stable-channel-update-for-desktop_16.html
- https://security.gentoo.org/glsa/202104-08
- https://crbug.com/1172192
