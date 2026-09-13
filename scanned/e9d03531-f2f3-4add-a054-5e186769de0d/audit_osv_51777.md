# [H] CVE-2021-4028

## Summary
Severity: High
Advisory: CVE-2021-4028
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4028
Type: osv

## Details
A flaw in the Linux kernel's implementation of RDMA communications manager listener code allowed an attacker with local access to setup a socket to listen on a high port allowing for a list element to be used after free. Given the ability to execute code, a local attacker could leverage this use-after-free to crash the system or possibly escalate privileges on the system.

## References
- https://security.netapp.com/advisory/ntap-20221228-0002/
- https://access.redhat.com/security/cve/CVE-2021-4028
- https://bugzilla.redhat.com/show_bug.cgi?id=2027201
- https://bugzilla.suse.com/show_bug.cgi?id=1193167#c0
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=bc0bdc5afaa74
- https://lkml.org/lkml/2021/10/4/697
