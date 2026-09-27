# [H] CVE-2020-15971

## Summary
Severity: High
Advisory: CVE-2020-15971
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-03
Source: https://osv.dev/vulnerability/CVE-2020-15971
Type: osv

## Details
Use after free in printing in Google Chrome prior to 86.0.4240.75 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/24QFL4C3AZKMFVL7LVSYMU2DNE5VVUGS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4GWCWNHTTYOH6HSFUXPGPBB6J6JYZHZE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SC3U3H6AISVZB5PLZLLNF4HMQ4UFFL7M/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00016.html
- https://chromereleases.googleblog.com/2020/10/stable-channel-update-for-desktop.html
- https://www.debian.org/security/2021/dsa-4824
- https://crbug.com/1114062
