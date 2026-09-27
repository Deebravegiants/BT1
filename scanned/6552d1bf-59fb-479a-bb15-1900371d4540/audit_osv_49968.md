# [M] CVE-2019-5778

## Summary
Severity: Medium
Advisory: CVE-2019-5778
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-02-19
Source: https://osv.dev/vulnerability/CVE-2019-5778
Type: osv

## Details
A missing case for handling special schemes in permission request checks in Extensions in Google Chrome prior to 72.0.3626.81 allowed an attacker who convinced a user to install a malicious extension to bypass extension permission checks for privileged pages via a crafted Chrome Extension.

## References
- http://www.securityfocus.com/bid/106767
- https://crbug.com/918470
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JVFHYCJGMZQUKYSIE2BXE4NLEGFGUXU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQOP53LXXPRGD4N5OBKGQTSMFXT32LF6/
- https://www.debian.org/security/2019/dsa-4395
- https://access.redhat.com/errata/RHSA-2019:0309
- https://chromereleases.googleblog.com/2019/01/stable-channel-update-for-desktop.html
