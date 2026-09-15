# [H] CVE-2021-26708

## Summary
Severity: High
Advisory: CVE-2021-26708
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-05
Source: https://osv.dev/vulnerability/CVE-2021-26708
Type: osv

## Details
A local privilege escalation was discovered in the Linux kernel before 5.10.13. Multiple race conditions in the AF_VSOCK implementation are caused by wrong locking in net/vmw_vsock/af_vsock.c. The race conditions were implicitly introduced in the commits that added VSOCK multi-transport support.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.13
- http://www.openwall.com/lists/oss-security/2021/02/05/6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c518adafa39f37858697ac9309c6cf1805581446
- https://security.netapp.com/advisory/ntap-20210312-0008/
- https://www.openwall.com/lists/oss-security/2021/02/04/5
- http://www.openwall.com/lists/oss-security/2021/04/09/2
- http://www.openwall.com/lists/oss-security/2022/01/25/14
