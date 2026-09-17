# [H] CVE-2021-21198

## Summary
Severity: High
Advisory: CVE-2021-21198
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2021-04-09
Source: https://osv.dev/vulnerability/CVE-2021-21198
Type: osv

## Details
Out of bounds read in IPC in Google Chrome prior to 89.0.4389.114 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EAJ42L4JFPBJATCZ7MOZQTUDGV4OEHHG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U3GZ42MYPGD35V652ZPVPYYS7A7LVXVY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUZBGKGVZADNA3I24NVG7HAYYUTOSN5A/
- https://security.gentoo.org/glsa/202104-08
- http://packetstormsecurity.com/files/162973/Chrome-Legacy-ipc-Message-Passed-Via-Shared-Memory.html
- https://chromereleases.googleblog.com/2021/03/stable-channel-update-for-desktop_30.html
- https://crbug.com/1184399
