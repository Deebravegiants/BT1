# [C] CVE-2020-6573

## Summary
Severity: Critical
Advisory: CVE-2020-6573
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-09-21
Source: https://osv.dev/vulnerability/CVE-2020-6573
Type: osv

## Details
Use after free in video in Google Chrome on Android prior to 85.0.4183.102 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FN7HZIGAOCZKBT4LV363BCPRA5FLY25I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GNIYFJST4TFJYFZ27VODBOINCLBGULTD/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00049.html
- https://chromereleases.googleblog.com/2020/09/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202101-30
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00081.html
- https://www.debian.org/security/2021/dsa-4824
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00072.html
- https://crbug.com/1116304
