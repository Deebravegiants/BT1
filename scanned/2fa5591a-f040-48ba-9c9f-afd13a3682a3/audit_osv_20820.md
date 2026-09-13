# [H] CVE-2021-3743

## Summary
Severity: High
Advisory: CVE-2021-3743
Aliases: A-224080927, PUB-A-224080927
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3743
Type: osv

## Details
An out-of-bounds (OOB) memory read flaw was found in the Qualcomm IPC router protocol in the Linux kernel. A missing sanity check allows a local attacker to gain access to out-of-bounds memory, leading to a system crash or a leak of internal kernel information. The highest threat from this vulnerability is to system availability.

## References
- https://security.netapp.com/advisory/ntap-20220407-0007/
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=7e78c597c3eb
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7e78c597c3ebfd0cb329aa09a838734147e4f117
- https://github.com/torvalds/linux/commit/7e78c597c3ebfd0cb329aa09a838734147e4f117
- https://www.openwall.com/lists/oss-security/2021/08/27/2
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1997961
- https://lists.openwall.net/netdev/2021/08/17/124
