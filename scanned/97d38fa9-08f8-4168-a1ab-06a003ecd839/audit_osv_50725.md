# [M] CVE-2020-35508

## Summary
Severity: Medium
Advisory: CVE-2020-35508
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2020-35508
Type: osv

## Details
A flaw possibility of race condition and incorrect initialization of the process id was found in the Linux kernel child/parent process identification handling while filtering signal handlers. A local attacker is able to abuse this flaw to bypass checks to send any signal to a privileged process.

## References
- https://security.netapp.com/advisory/ntap-20210513-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1902724
- https://github.com/torvalds/linux/commit/b4e00444cab4c3f3fec876dc0cccc8cbb0d1a948
