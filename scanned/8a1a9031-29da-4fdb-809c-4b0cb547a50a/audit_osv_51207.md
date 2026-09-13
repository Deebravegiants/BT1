# [H] CVE-2021-21207

## Summary
Severity: High
Advisory: CVE-2021-21207
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-21207
Type: osv

## Details
Use after free in IndexedDB in Google Chrome prior to 90.0.4430.72 allowed an attacker who convinced a user to install a malicious extension to potentially perform a sandbox escape via a crafted Chrome Extension.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EAJ42L4JFPBJATCZ7MOZQTUDGV4OEHHG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U3GZ42MYPGD35V652ZPVPYYS7A7LVXVY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUZBGKGVZADNA3I24NVG7HAYYUTOSN5A/
- https://security.gentoo.org/glsa/202104-08
- https://www.debian.org/security/2021/dsa-4906
- https://chromereleases.googleblog.com/2021/04/stable-channel-update-for-desktop_14.html
- https://crbug.com/1185732
