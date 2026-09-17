# [H] CVE-2021-47505

## Summary
Severity: High
Advisory: CVE-2021-47505
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47505
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

aio: fix use-after-free due to missing POLLFREE handling

signalfd_poll() and binder_poll() are special in that they use a
waitqueue whose lifetime is the current task, rather than the struct
file as is normally the case.  This is okay for blocking polls, since a
blocking poll occurs within one task; however, non-blocking polls
require another solution.  This solution is for the queue to be cleared
before it is freed, by sending a POLLFREE notification to all waiters.

Unfortunately, only eventpoll handles POLLFREE.  A second type of
non-blocking poll, aio poll, was added in kernel v4.18, and it doesn't
handle POLLFREE.  This allows a use-after-free to occur if a signalfd or
binder fd is polled with aio poll, and the waitqueue gets freed.

Fix this by making aio poll handle POLLFREE.

A patch by Ramji Jiyani <ramjiyani@google.com>
(https://lore.kernel.org/r/20211027011834.2497484-1-ramjiyani@google.com)
tried to do this by making aio_poll_wake() always complete the request
inline if POLLFREE is seen.  However, that solution had two bugs.
First, it introduced a deadlock, as it unconditionally locked the aio
context while holding the waitqueue lock, which inverts the normal
locking order.  Second, it didn't consider that POLLFREE notifications
are missed while the request has been temporarily de-queued.

The second problem was solved by my previous patch.  This patch then
properly fixes the use-after-free by handling POLLFREE in a
deadlock-free way.  It does this by taking advantage of the fact that
freeing of the waitqueue is RCU-delayed, similar to what eventpoll does.

## References
- https://git.kernel.org/stable/c/4105e6a128e8a98455dfc9e6dbb2ab0c33c4497f
- https://git.kernel.org/stable/c/47ffefd88abfffe8a040bcc1dd0554d4ea6f7689
- https://git.kernel.org/stable/c/50252e4b5e989ce64555c7aef7516bdefc2fea72
- https://git.kernel.org/stable/c/60d311f9e6381d779d7d53371f87285698ecee24
- https://git.kernel.org/stable/c/321fba81ec034f88aea4898993c1bf15605c023f
