# [M] CVE-2021-47603

## Summary
Severity: Medium
Advisory: CVE-2021-47603
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47603
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: improve robustness of the audit queue handling

If the audit daemon were ever to get stuck in a stopped state the
kernel's kauditd_thread() could get blocked attempting to send audit
records to the userspace audit daemon.  With the kernel thread
blocked it is possible that the audit queue could grow unbounded as
certain audit record generating events must be exempt from the queue
limits else the system enter a deadlock state.

This patch resolves this problem by lowering the kernel thread's
socket sending timeout from MAX_SCHEDULE_TIMEOUT to HZ/10 and tweaks
the kauditd_send_queue() function to better manage the various audit
queues when connection problems occur between the kernel and the
audit daemon.  With this patch, the backlog may temporarily grow
beyond the defined limits when the audit daemon is stopped and the
system is under heavy audit pressure, but kauditd_thread() will
continue to make progress and drain the queues as it would for other
connection problems.  For example, with the audit daemon put into a
stopped state and the system configured to audit every syscall it
was still possible to shutdown the system without a kernel panic,
deadlock, etc.; granted, the system was slow to shutdown but that is
to be expected given the extreme pressure of recording every syscall.

The timeout value of HZ/10 was chosen primarily through
experimentation and this developer's "gut feeling".  There is likely
no one perfect value, but as this scenario is limited in scope (root
privileges would be needed to send SIGSTOP to the audit daemon), it
is likely not worth exposing this as a tunable at present.  This can
always be done at a later date if it proves necessary.

## References
- https://git.kernel.org/stable/c/4cc6badff97f74d0fce65f9784b5df3b64e4250b
- https://git.kernel.org/stable/c/75fdb751f84727d614deea0571a1490c3225d83a
- https://git.kernel.org/stable/c/8389f50ceb854cb437fefb9330d5024ed3c7c1f5
- https://git.kernel.org/stable/c/a5f4d17daf2e6cd7c1d9676b476147f6b4ac53f2
- https://git.kernel.org/stable/c/f4b3ee3c85551d2d343a3ba159304066523f730f
- https://git.kernel.org/stable/c/0d3277eabd542fb662be23696e5ec9f390d688e1
