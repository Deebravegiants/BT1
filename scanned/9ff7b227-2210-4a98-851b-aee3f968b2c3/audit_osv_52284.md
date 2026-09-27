# [H] CVE-2021-47281

## Summary
Severity: High
Advisory: CVE-2021-47281
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47281
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: seq: Fix race of snd_seq_timer_open()

The timer instance per queue is exclusive, and snd_seq_timer_open()
should have managed the concurrent accesses.  It looks as if it's
checking the already existing timer instance at the beginning, but
it's not right, because there is no protection, hence any later
concurrent call of snd_seq_timer_open() may override the timer
instance easily.  This may result in UAF, as the leftover timer
instance can keep running while the queue itself gets closed, as
spotted by syzkaller recently.

For avoiding the race, add a proper check at the assignment of
tmr->timeri again, and return -EBUSY if it's been already registered.

## References
- https://git.kernel.org/stable/c/bd7d88b0874f82f7b29d1a53e574cedaf23166ba
- https://git.kernel.org/stable/c/536a7646c00a0f14fee49e5e313109e5da2f6031
- https://git.kernel.org/stable/c/83e197a8414c0ba545e7e3916ce05f836f349273
