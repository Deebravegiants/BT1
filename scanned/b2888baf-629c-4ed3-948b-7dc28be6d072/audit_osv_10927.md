# [H] CVE-2017-5130

## Summary
Severity: High
Advisory: CVE-2017-5130
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2017-5130
Type: osv

## Details
An integer overflow in xmlmemory.c in libxml2 before 2.9.5, as used in Google Chrome prior to 62.0.3202.62 and other products, allowed a remote attacker to potentially exploit heap corruption via a crafted XML file.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00004.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/101482
- https://access.redhat.com/errata/RHSA-2017:2997
- https://chromereleases.googleblog.com/2017/10/stable-channel-update-for-desktop.html
- https://crbug.com/722079
- https://git.gnome.org/browse/libxml2/commit/?id=897dffbae322b46b83f99a607d527058a72c51ed
- https://lists.debian.org/debian-lts-announce/2017/11/msg00034.html
- https://security.gentoo.org/glsa/201710-24
- https://security.netapp.com/advisory/ntap-20190719-0001/
- http://bugzilla.gnome.org/show_bug.cgi?id=783026
