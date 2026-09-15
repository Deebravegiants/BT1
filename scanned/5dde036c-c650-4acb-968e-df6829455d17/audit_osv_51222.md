# [M] CVE-2021-21222

## Summary
Severity: Medium
Advisory: CVE-2021-21222
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-21222
Type: osv

## Details
Heap buffer overflow in V8 in Google Chrome prior to 90.0.4430.85 allowed a remote attacker who had compromised the renderer process to bypass site isolation via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EAJ42L4JFPBJATCZ7MOZQTUDGV4OEHHG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U3GZ42MYPGD35V652ZPVPYYS7A7LVXVY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUZBGKGVZADNA3I24NVG7HAYYUTOSN5A/
- https://chromereleases.googleblog.com/2021/04/stable-channel-update-for-desktop_20.html
- https://crbug.com/1194046
- https://security.gentoo.org/glsa/202104-08
- https://www.debian.org/security/2021/dsa-4906
