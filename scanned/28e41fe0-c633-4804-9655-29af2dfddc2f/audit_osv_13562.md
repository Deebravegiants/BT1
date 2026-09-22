# [H] CVE-2018-20346

## Summary
Severity: High
Advisory: CVE-2018-20346
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20346
Type: osv

## Details
SQLite before 3.25.3, when the FTS3 extension is enabled, encounters an integer overflow (and resultant buffer overflow) for FTS3 queries that occur after crafted changes to FTS3 shadow tables, allowing remote attackers to execute arbitrary code by leveraging the ability to run arbitrary SQL statements (such as in certain WebSQL use cases), aka Magellan.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU4NZ6DDU4BEM3ACM3FM6GLEPX56ZQXK/
- https://support.apple.com/HT209443
- https://support.apple.com/HT209446
- https://support.apple.com/HT209447
- https://support.apple.com/HT209448
- https://support.apple.com/HT209450
- https://support.apple.com/HT209451
- https://usn.ubuntu.com/4019-1/
- https://usn.ubuntu.com/4019-2/
- https://www.mail-archive.com/sqlite-users%40mailinglists.sqlite.org/msg113218.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00070.html
- http://www.securityfocus.com/bid/106323
- https://access.redhat.com/articles/3758321
- https://blade.tencent.com/magellan/index_en.html
- https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html
- https://chromium.googlesource.com/chromium/src/+/c368e30ae55600a1c3c9cb1710a54f9c55de786e
