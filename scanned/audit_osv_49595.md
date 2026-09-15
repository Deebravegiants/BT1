# [H] CVE-2019-13767

## Summary
Severity: High
Advisory: CVE-2019-13767
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-10
Source: https://osv.dev/vulnerability/CVE-2019-13767
Type: osv

## Details
Use after free in media picker in Google Chrome prior to 79.0.3945.88 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N5CIQCVS6E3ULJCNU7YJXJPO2BLQZDTK/
- https://seclists.org/bugtraq/2020/Jan/27
- https://security.gentoo.org/glsa/202003-08
- https://www.debian.org/security/2020/dsa-4606
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00005.html
- http://packetstormsecurity.com/files/156563/Chrome-DesktopMediaPickerController-WebContentsDestroyed-Use-After-Free.html
- https://chromereleases.googleblog.com/2019/12/stable-channel-update-for-desktop_17.html
- https://crbug.com/1031653
