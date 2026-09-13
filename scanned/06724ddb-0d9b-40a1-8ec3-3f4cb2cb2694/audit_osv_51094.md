# [M] CVE-2021-20265

## Summary
Severity: Medium
Advisory: CVE-2021-20265
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2021-20265
Type: osv

## Details
A flaw was found in the way memory resources were freed in the unix_stream_recvmsg function in the Linux kernel when a signal was pending. This flaw allows an unprivileged local user to crash the system by exhausting available memory. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1908827
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fa0dc04df259ba2df3ce1920e9690c7842f8fa4b
- https://www.oracle.com/security-alerts/cpuoct2021.html
