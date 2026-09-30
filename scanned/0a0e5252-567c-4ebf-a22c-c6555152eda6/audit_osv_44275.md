# [H] ALSA: pcm: wake linked drain waiters on unlink

## Summary
Severity: High
Advisory: CVE-2026-80716
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: wake linked drain waiters on unlink

snd_pcm_drain() on a linked stream parks an on-stack wait entry on the
drained peer's runtime->sleep, and after schedule_timeout() removes it
only if that peer is still found in the caller's group.  If group
membership changes during the wait and the sleep ends by signal or
timeout (so autoremove_wake_function() does not run), finish_wait() is
skipped and snd_pcm_drain() returns with the entry still queued on that
stream's sleep list; a later wake_up() then walks a freed stack frame.
This is reachable by unlinking either the drained or the draining stream.

Unlike the close path (snd_pcm_drop() -> snd_pcm_post_stop()),
snd_pcm_unlink() never wakes the sleep queues.  Wake every group member
under the group lock before the membership change, so a linked drainer is
released and drops its entry while the streams are still grouped.

The window was opened when snd_pcm_link_rwsem stopped being held across
the wait and the removal became conditional on group membership (see
Fixes). The later switch to finish_wait() kept that conditional removal,
so the signal/timeout case remained.

## References
- https://git.kernel.org/stable/c/1c1b7e8e545ce65e40f65b55c432765e058ea98f
- https://git.kernel.org/stable/c/2940cc3cf43c72126b74ee6376314c195382023a
- https://git.kernel.org/stable/c/3035bb784cea3f338934f5042dd3f35225a51b2e
- https://git.kernel.org/stable/c/c172e4c53321ee6429955295ea133bc3597a3ca9
- https://git.kernel.org/stable/c/db09bc4ab19ce548a078240d2374792523953500
- https://git.kernel.org/stable/c/e8315330e4ec09c0cac625515400e13d0ee22b81
- https://git.kernel.org/stable/c/e8b784a3f4fba3ea9c4d05138ecfa784a069627f
- https://git.kernel.org/stable/c/f495b6c4c8594122918552c9be2b51eb71647cd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80716.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
