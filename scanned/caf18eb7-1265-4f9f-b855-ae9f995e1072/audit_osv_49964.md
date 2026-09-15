# [H] CVE-2019-5774

## Summary
Severity: High
Advisory: CVE-2019-5774
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-19
Source: https://osv.dev/vulnerability/CVE-2019-5774
Type: osv

## Details
Omission of the .desktop filetype from the Safe Browsing checklist in SafeBrowsing in Google Chrome on Linux prior to 72.0.3626.81 allowed an attacker who convinced a user to download a .desktop file to execute arbitrary code via a downloaded .desktop file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JVFHYCJGMZQUKYSIE2BXE4NLEGFGUXU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQOP53LXXPRGD4N5OBKGQTSMFXT32LF6/
- http://www.securityfocus.com/bid/106767
- https://crbug.com/904182
- https://www.debian.org/security/2019/dsa-4395
- https://access.redhat.com/errata/RHSA-2019:0309
- https://chromereleases.googleblog.com/2019/01/stable-channel-update-for-desktop.html
