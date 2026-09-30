# [H] CVE-2017-5972

## Summary
Severity: High
Advisory: CVE-2017-5972
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-14
Source: https://osv.dev/vulnerability/CVE-2017-5972
Type: osv

## Details
The TCP stack in the Linux kernel 3.x does not properly implement a SYN cookie protection mechanism for the case of a fast network connection, which allows remote attackers to cause a denial of service (CPU consumption) by sending many TCP SYN packets, as demonstrated by an attack against the kernel-3.10.0 package in CentOS Linux 7. NOTE: third parties have been unable to discern any relationship between the GitHub Engineering finding and the Trigemini.c attack code.

## References
- https://www.exploit-db.com/exploits/41350/
- http://seclists.org/oss-sec/2017/q1/573
- http://www.securityfocus.com/bid/96231
- https://access.redhat.com/security/cve/cve-2017-5972
- https://githubengineering.com/syn-flood-mitigation-with-synsanity/
- https://security-tracker.debian.org/tracker/CVE-2017-5972
- https://bugzilla.redhat.com/show_bug.cgi?id=1422081
- https://cxsecurity.com/issue/WLB-2017020112
- https://packetstormsecurity.com/files/141083/CentOS7-Kernel-Denial-Of-Service.html
