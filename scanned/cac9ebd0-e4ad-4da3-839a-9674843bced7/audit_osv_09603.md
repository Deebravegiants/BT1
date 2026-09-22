# [M] CVE-2017-1000367

## Summary
Severity: Medium
Advisory: CVE-2017-1000367
CVSS: 6.4 (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-1000367
Type: osv

## Details
Todd Miller's sudo version 1.8.20 and earlier is vulnerable to an input validation (embedded spaces) in the get_process_ttyname() function resulting in information disclosure and command execution.

## References
- http://www.openwall.com/lists/oss-security/2022/12/22/5
- http://www.openwall.com/lists/oss-security/2022/12/22/6
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VXEXC4NNIG2QOZY6N2YUK246KI3D3UQO/
- http://lists.opensuse.org/opensuse-security-announce/2017-05/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2017-05/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2017-05/msg00079.html
- http://seclists.org/fulldisclosure/2017/Jun/3
- http://www.debian.org/security/2017/dsa-3867
- http://www.securityfocus.com/bid/98745
- http://www.ubuntu.com/usn/USN-3304-1
- https://access.redhat.com/errata/RHSA-2017:1381
- https://access.redhat.com/errata/RHSA-2017:1382
- https://security.gentoo.org/glsa/201705-15
- https://www.exploit-db.com/exploits/42183/
- https://www.sudo.ws/alerts/linux_tty.html
- http://packetstormsecurity.com/files/142783/Sudo-get_process_ttyname-Race-Condition.html
- http://www.openwall.com/lists/oss-security/2017/05/30/16
- http://www.securitytracker.com/id/1038582
