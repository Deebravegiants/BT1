# [H] CVE-2016-3993

## Summary
Severity: High
Advisory: CVE-2016-3993
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-3993
Type: osv

## Details
Off-by-one error in the __imlib_MergeUpdate function in lib/updates.c in imlib2 before 1.4.9 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via crafted coordinates.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00076.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=819818
- https://git.enlightenment.org/legacy/imlib2.git/commit/?id=ce94edca1ccfbe314cb7cd9453433fad404ec7ef
- https://sourceforge.net/p/enlightenment/mailman/message/35055012/
- http://www.debian.org/security/2016/dsa-3555
