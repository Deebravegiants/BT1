# [H] CVE-2021-4083

## Summary
Severity: High
Advisory: CVE-2021-4083
Aliases: A-216408350, ASB-A-216408350, PUB-A-216408350
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-18
Source: https://osv.dev/vulnerability/CVE-2021-4083
Type: osv

## Details
A read-after-free memory flaw was found in the Linux kernel's garbage collection for Unix domain socket file handlers in the way users call close() and fget() simultaneously and can potentially trigger a race condition. This flaw allows a local user to crash the system or escalate their privileges on the system. This flaw affects Linux kernel versions prior to 5.16-rc4.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20220217-0005/
- https://www.debian.org/security/2022/dsa-5096
- https://bugzilla.redhat.com/show_bug.cgi?id=2029923
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=054aa8d439b9
- https://www.oracle.com/security-alerts/cpujul2022.html
