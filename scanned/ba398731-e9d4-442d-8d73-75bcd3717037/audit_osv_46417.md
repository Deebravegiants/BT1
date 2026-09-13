# [H] CVE-2010-0302

## Summary
Severity: High
Advisory: CVE-2010-0302
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2010-03-05
Source: https://osv.dev/vulnerability/CVE-2010-0302
Type: osv

## Details
Use-after-free vulnerability in the abstract file-descriptor handling interface in the cupsdDoSelect function in scheduler/select.c in the scheduler in cupsd in CUPS before 1.4.4, when kqueue or epoll is used, allows remote attackers to cause a denial of service (daemon crash or hang) via a client disconnection during listing of a large number of print jobs, related to improperly maintaining a reference count. NOTE: some of these details are obtained from third party information. NOTE: this vulnerability exists because of an incomplete fix for CVE-2009-3553.

## References
- http://cups.org/articles.php?L596
- http://cups.org/str.php?L3490
- http://secunia.com/advisories/38785
- http://secunia.com/advisories/38927
- http://secunia.com/advisories/38979
- http://secunia.com/advisories/40220
- http://security.gentoo.org/glsa/glsa-201207-10.xml
- http://support.apple.com/kb/HT4188
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:073
- http://www.securityfocus.com/bid/38510
- http://www.securitytracker.com/id?1024124
- http://www.ubuntu.com/usn/USN-906-1
- http://www.vupen.com/english/advisories/2010/1481
- https://rhn.redhat.com/errata/RHSA-2010-0129.html
- http://lists.apple.com/archives/security-announce/2010//Jun/msg00001.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-March/037174.html
- https://bugzilla.redhat.com/show_bug.cgi?id=557775
- https://bugzilla.redhat.com/show_bug.cgi?id=557775
- http://www.securityfocus.com/bid/38510
- http://www.securitytracker.com/id?1024124
