# [H] CVE-2017-1000083

## Summary
Severity: High
Advisory: CVE-2017-1000083
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-1000083
Type: osv

## Details
backend/comics/comics-document.c (aka the comic book backend) in GNOME Evince before 3.24.1 allows remote attackers to execute arbitrary commands via a .cbt file that is a TAR archive containing a filename beginning with a "--" command-line option substring, as demonstrated by a --checkpoint-action=exec=bash at the beginning of the filename.

## References
- http://seclists.org/oss-sec/2017/q3/128
- http://www.debian.org/security/2017/dsa-3911
- http://www.securityfocus.com/bid/99597
- https://access.redhat.com/errata/RHSA-2017:2388
- https://bugzilla.gnome.org/show_bug.cgi?id=784630
- https://github.com/GNOME/evince/commit/717df38fd8509bf883b70d680c9b1b3cf36732ee
- https://www.exploit-db.com/exploits/45824/
- https://www.exploit-db.com/exploits/46341/
