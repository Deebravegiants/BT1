# [H] CVE-2018-14633

## Summary
Severity: High
Advisory: CVE-2018-14633
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2018-09-25
Source: https://osv.dev/vulnerability/CVE-2018-14633
Type: osv

## Details
A security flaw was found in the chap_server_compute_md5() function in the ISCSI target code in the Linux kernel in a way an authentication request from an ISCSI initiator is processed. An unauthenticated remote attacker can cause a stack buffer overflow and smash up to 17 bytes of the stack. The attack requires the iSCSI target to be enabled on the victim host. Depending on how the target's code was built (i.e. depending on a compiler, compile flags and hardware architecture) an attack may lead to a system crash and thus to a denial-of-service or possibly to a non-authorized access to data exported by an iSCSI target. Due to the nature of the flaw, privilege escalation cannot be fully ruled out, although we believe it is highly unlikely. Kernel versions 4.18.x, 4.14.x and 3.10.x are believed to be vulnerable.

## References
- http://www.securityfocus.com/bid/105388
- https://access.redhat.com/errata/RHSA-2018:3651
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://www.debian.org/security/2018/dsa-4308
- https://usn.ubuntu.com/3775-2/
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3777-1/
- https://usn.ubuntu.com/3777-2/
- https://access.redhat.com/errata/RHSA-2019:1946
- https://usn.ubuntu.com/3775-1/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-3/
- https://access.redhat.com/errata/RHSA-2018:3666
- https://seclists.org/oss-sec/2018/q3/270
- https://usn.ubuntu.com/3779-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/mkp/scsi.git/commit/?h=4.19/scsi-fixes&id=8c39e2699f8acb2e29782a834e56306da24937fe
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14633
- https://git.kernel.org/pub/scm/linux/kernel/git/mkp/scsi.git/commit/?h=4.19/scsi-fixes&id=1816494330a83f2a064499d8ed2797045641f92c
