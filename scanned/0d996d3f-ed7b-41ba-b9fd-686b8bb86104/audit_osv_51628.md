# [H] CVE-2021-3640

## Summary
Severity: High
Advisory: CVE-2021-3640
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2021-3640
Type: osv

## Details
A flaw use-after-free in function sco_sock_sendmsg() of the Linux kernel HCI subsystem was found in the way user calls ioct UFFDIO_REGISTER or other way triggers race condition of the call sco_conn_del() together with the call sco_sock_sendmsg() with the expected controllable faulting memory page. A privileged local user could use this flaw to crash the system or escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://security.netapp.com/advisory/ntap-20220419-0003/
- https://www.debian.org/security/2022/dsa-5096
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://ubuntu.com/security/CVE-2021-3640
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/net/bluetooth/sco.c?h=v5.16&id=99c23da0eed4fd20cae8243f2b51e10e66aa0951
- https://github.com/torvalds/linux/commit/99c23da0eed4fd20cae8243f2b51e10e66aa0951
- https://bugzilla.redhat.com/show_bug.cgi?id=1980646
- https://www.openwall.com/lists/oss-security/2021/07/22/1
