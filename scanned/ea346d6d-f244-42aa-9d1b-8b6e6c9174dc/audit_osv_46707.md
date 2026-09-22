# [H] CVE-2014-9771

## Summary
Severity: High
Advisory: CVE-2014-9771
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2014-9771
Type: osv

## Details
Integer overflow in imlib2 before 1.4.7 allows remote attackers to cause a denial of service (memory consumption or application crash) via a crafted image, which triggers an invalid read operation.

## References
- http://www.debian.org/security/2016/dsa-3555
- https://bugzilla.redhat.com/show_bug.cgi?id=1324774
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00076.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=820206
- https://git.enlightenment.org/legacy/imlib2.git/commit/?id=143f299
- https://git.enlightenment.org/legacy/imlib2.git/tree/ChangeLog
