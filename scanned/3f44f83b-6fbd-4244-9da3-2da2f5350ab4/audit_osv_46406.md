# [H] CVE-2009-3611

## Summary
Severity: High
Advisory: CVE-2009-3611
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2009-10-26
Source: https://osv.dev/vulnerability/CVE-2009-3611
Type: osv

## Details
common/snapshots.py in Back In Time (aka backintime) 0.9.26 changes certain permissions to 0777 before deleting the files in an old backup snapshot, which allows local users to obtain sensitive information by reading these files, or interfere with backup integrity by modifying files that are shared across snapshots.

## References
- https://bugs.launchpad.net/ubuntu/+source/backintime/+bug/434256
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=543785
- http://marc.info/?l=oss-security&m=125553645511436&w=2
- http://marc.info/?l=oss-security&m=125554894700336&w=2
- https://www.redhat.com/archives/fedora-package-announce/2009-September/msg00821.html
- https://www.redhat.com/archives/fedora-package-announce/2009-September/msg00823.html
- http://bugs.gentoo.org/show_bug.cgi?id=289047
- http://ftp.debian.org/debian/pool/main/b/backintime/backintime_0.9.26-3.diff.gz
- http://bugs.gentoo.org/show_bug.cgi?id=289047
- https://bugzilla.redhat.com/show_bug.cgi?id=520210
- http://ftp.debian.org/debian/pool/main/b/backintime/backintime_0.9.26-3.diff.gz
