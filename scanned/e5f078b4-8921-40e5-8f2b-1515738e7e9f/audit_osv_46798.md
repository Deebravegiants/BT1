# [M] CVE-2015-3238

## Summary
Severity: Medium
Advisory: CVE-2015-3238
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2015-08-24
Source: https://osv.dev/vulnerability/CVE-2015-3238
Type: osv

## Details
The _unix_run_helper_binary function in the pam_unix module in Linux-PAM (aka pam) before 1.2.1, when unable to directly access passwords, allows local users to enumerate usernames or cause a denial of service (hang) via a large password.

## References
- http://rhn.redhat.com/errata/RHSA-2015-1640.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.ubuntu.com/usn/USN-2935-1
- http://www.ubuntu.com/usn/USN-2935-2
- http://www.ubuntu.com/usn/USN-2935-3
- https://security.gentoo.org/glsa/201605-05
- https://www.trustwave.com/Resources/Security-Advisories/Advisories/TWSL2015-011/?fid=6551
- https://www.trustwave.com/Resources/SpiderLabs-Blog/Username-Enumeration-against-OpenSSH-SELinux-with-CVE-2015-3238/
- https://bugzilla.redhat.com/show_bug.cgi?id=1228571
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161350.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-June/161249.html
- http://www.openwall.com/lists/oss-security/2015/06/25/13
- http://www.securityfocus.com/bid/75428
