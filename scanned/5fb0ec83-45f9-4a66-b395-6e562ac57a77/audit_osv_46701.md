# [C] CVE-2014-9761

## Summary
Severity: Critical
Advisory: CVE-2014-9761
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/CVE-2014-9761
Type: osv

## Details
Multiple stack-based buffer overflows in the GNU C Library (aka glibc or libc6) before 2.23 allow context-dependent attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a long argument to the (1) nan, (2) nanf, or (3) nanl function.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0680.html
- http://www.ubuntu.com/usn/USN-2985-1
- http://www.ubuntu.com/usn/USN-2985-2
- https://access.redhat.com/errata/RHSA-2017:1916
- https://security.gentoo.org/glsa/201702-11
- https://www.sourceware.org/ml/libc-alpha/2016-02/msg00502.html
- https://sourceware.org/bugzilla/show_bug.cgi?id=16962
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184626.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00042.html
- http://packetstormsecurity.com/files/153278/WAGO-852-Industrial-Managed-Switch-Series-Code-Execution-Hardcoded-Credentials.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://www.openwall.com/lists/oss-security/2016/01/19/11
- http://www.openwall.com/lists/oss-security/2016/01/20/1
- http://www.securityfocus.com/bid/83306
