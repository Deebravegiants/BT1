# [C] CVE-2017-16548

## Summary
Severity: Critical
Advisory: CVE-2017-16548
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-06
Source: https://osv.dev/vulnerability/CVE-2017-16548
Type: osv

## Details
The receive_xattr function in xattrs.c in rsync 3.1.2 and 3.1.3-development does not check for a trailing '\0' character in an xattr name, which allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact by sending crafted data to the daemon.

## References
- https://git.samba.org/rsync.git/?p=rsync.git%3Ba=commit%3Bh=47a63d90e71d3e19e0e96052bb8c6b9cb140ecc1
- https://lists.debian.org/debian-lts-announce/2017/12/msg00020.html
- https://usn.ubuntu.com/3543-1/
- https://usn.ubuntu.com/3543-2/
- https://www.debian.org/security/2017/dsa-4068
- https://bugzilla.samba.org/show_bug.cgi?id=13112
