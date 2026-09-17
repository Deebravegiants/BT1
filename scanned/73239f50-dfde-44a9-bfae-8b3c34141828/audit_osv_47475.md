# [H] CVE-2016-6232

## Summary
Severity: High
Advisory: CVE-2016-6232
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/CVE-2016-6232
Type: osv

## Details
Directory traversal vulnerability in KArchive before 5.24, as used in KDE Frameworks, allows remote attackers to write to arbitrary files via a ../ (dot dot slash) in a filename in an archive file, related to KNewsstuff downloads.

## References
- http://www.openwall.com/lists/oss-security/2016/07/16/2
- http://www.securityfocus.com/bid/91806
- https://quickgit.kde.org/?p=karchive.git&a=commit&h=0cb243f64eef45565741b27364cece7d5c349c37
- https://usn.ubuntu.com/4100-1/
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00000.html
- http://www.debian.org/security/2016/dsa-3643
- http://www.openwall.com/lists/oss-security/2016/07/16/3
- http://www.ubuntu.com/usn/USN-3042-1
- https://www.kde.org/info/security/advisory-20160724-1.txt
