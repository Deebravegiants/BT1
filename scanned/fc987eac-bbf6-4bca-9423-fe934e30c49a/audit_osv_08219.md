# [H] CVE-2016-1541

## Summary
Severity: High
Advisory: CVE-2016-1541
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-07
Source: https://osv.dev/vulnerability/CVE-2016-1541
Type: osv

## Details
Heap-based buffer overflow in the zip_read_mac_metadata function in archive_read_support_format_zip.c in libarchive before 3.2.0 allows remote attackers to execute arbitrary code via crafted entry-size values in a ZIP archive.

## References
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00003.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00090.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/89355
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.352685
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3574
- http://www.kb.cert.org/vuls/id/862384
- http://www.ubuntu.com/usn/USN-2981-1
- https://security.gentoo.org/glsa/201701-03
- https://github.com/libarchive/libarchive/issues/656
- https://github.com/libarchive/libarchive/commit/d0331e8e5b05b475f20b1f3101fe1ad772d7e7e7
