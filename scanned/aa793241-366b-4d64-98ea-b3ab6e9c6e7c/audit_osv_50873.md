# [C] CVE-2020-6465

## Summary
Severity: Critical
Advisory: CVE-2020-6465
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-6465
Type: osv

## Details
Use after free in reader mode in Google Chrome on Android prior to 83.0.4103.61 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OQYH5OK7O4BU6E37WWG5SEEHV65BFSGR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WLFZ5N4EK6I4ZJP5YSKLLVN3ELXEB4XT/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00038.html
- https://chromereleases.googleblog.com/2020/05/stable-channel-update-for-desktop_19.html
- https://security.gentoo.org/glsa/202006-02
- https://www.debian.org/security/2020/dsa-4714
- https://crbug.com/1073015
