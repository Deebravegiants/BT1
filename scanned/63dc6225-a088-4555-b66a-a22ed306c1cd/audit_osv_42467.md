# [H] ALSA: timer: drain a slave's callback before its master detaches it

## Summary
Severity: High
Advisory: CVE-2026-68201
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68201
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: drain a slave's callback before its master detaches it

snd_timer_close_locked() drains the closing instance's own in-flight
callback (IFLG_CALLBACK) before freeing it, but not its slaves'. When a
master instance is closed, remove_slave_links() clears each slave's
->timer; the slave's own close then reads timer == NULL and takes the
branch that skips the drain entirely (snd_timer_stop_slave() also no-ops
on a NULL timer). So a slave whose callback is still running when the
master is closed is freed underneath the live callback, leading to
use-after-free.

Drain the slaves too before remove_slave_links() severs them.
snd_timer_stop() has already taken this instance off the active list, so
no new slave callback can be queued. Take the slaves off the ack list so
a pending one can't fire either, then wait for any that is already in
flight.

## References
- https://git.kernel.org/stable/c/2b298997786876b225cff2446e11a0fa6f602f6d
- https://git.kernel.org/stable/c/426c0ff1c433d6030610ad4f9375746dfe931caa
- https://git.kernel.org/stable/c/bdefe1346a8e6b8dc8593406dc2617e985fcbcab
- https://git.kernel.org/stable/c/cd461bcfcdf8d6b6b5365941c1d3859f8bc77aa0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
