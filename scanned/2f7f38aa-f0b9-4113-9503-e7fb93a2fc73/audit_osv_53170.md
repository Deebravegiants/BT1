# [H] CVE-2022-3176

## Summary
Severity: High
Advisory: CVE-2022-3176
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-16
Source: https://osv.dev/vulnerability/CVE-2022-3176
Type: osv

## Details
There exists a use-after-free in io_uring in the Linux kernel. Signalfd_poll() and binder_poll() use a waitqueue whose lifetime is the current task. It will send a POLLFREE notification to all waiters before the queue is freed. Unfortunately, the io_uring poll doesn't handle POLLFREE. This allows a use-after-free to occur if a signalfd or binder fd is polled with io_uring poll, and the waitqueue gets freed. We recommend upgrading past commit fc78b2fc21f10c4c9c4d5d659a685710ffa63659

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://security.netapp.com/advisory/ntap-20230216-0003/
- https://www.debian.org/security/2022/dsa-5257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit?h=linux-5.4.y&id=fc78b2fc21f10c4c9c4d5d659a685710ffa63659
- https://kernel.dance/#fc78b2fc21f10c4c9c4d5d659a685710ffa63659
