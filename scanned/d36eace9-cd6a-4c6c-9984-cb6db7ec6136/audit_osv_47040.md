# [C] CVE-2015-8779

## Summary
Severity: Critical
Advisory: CVE-2015-8779
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/CVE-2015-8779
Type: osv

## Details
Stack-based buffer overflow in the catopen function in the GNU C Library (aka glibc or libc6) before 2.23 allows context-dependent attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a long catalog name.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0680.html
- http://www.debian.org/security/2016/dsa-3480
- http://www.debian.org/security/2016/dsa-3481
- http://www.ubuntu.com/usn/USN-2985-1
- http://www.ubuntu.com/usn/USN-2985-2
- https://access.redhat.com/errata/RHSA-2017:1916
- https://security.gentoo.org/glsa/201602-02
- https://security.gentoo.org/glsa/201702-11
- https://www.sourceware.org/ml/libc-alpha/2016-02/msg00502.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=17905
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184626.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00042.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://www.openwall.com/lists/oss-security/2016/01/19/11
- http://www.openwall.com/lists/oss-security/2016/01/20/1
