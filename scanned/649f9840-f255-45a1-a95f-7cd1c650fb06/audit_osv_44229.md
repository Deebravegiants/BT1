# [H] ALSA: seq: oss: Serialize readq reset state with q->lock

## Summary
Severity: High
Advisory: CVE-2026-80628
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80628
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: seq: oss: Serialize readq reset state with q->lock

snd_seq_oss_readq_clear() resets qlen, head, and tail without
q->lock even though the normal reader and producer paths serialize the
same ring state under that spinlock. A reset can therefore race
snd_seq_oss_readq_free() or snd_seq_oss_readq_put_event() and leave
stale records in the queue, drop freshly queued ones, or report the
wrong readiness after wakeup. KCSAN reports a data race between
snd_seq_oss_readq_clear() and snd_seq_oss_readq_free().

Take q->lock while clearing the ring and resetting input_time. Factor
the enqueue logic into a caller-locked helper so
snd_seq_oss_readq_put_timestamp() updates its suppression state under
the same lock instead of racing the reset path.

The buggy scenario involves two paths, with each column showing the
order within that path:

reset path:                      locked readq updater:
1. snd_seq_oss_reset() or        1. A reader or callback producer
   release reaches                  takes q->lock on the same queue.
   snd_seq_oss_readq_clear().
2. snd_seq_oss_readq_clear()     2. The updater tests or modifies
   resets qlen, head, tail,         qlen, head, and tail.
   and input_time.
3. snd_seq_oss_readq_clear()     3. The updater completes its
   wakes sleepers on                read-modify-write sequence.
   q->midi_sleep.
4. Without q->lock, the reset    4. The resulting ring state drives
   can overlap the locked           later reads and readiness.
   update.

KCSAN reports:

BUG: KCSAN: data-race in snd_seq_oss_readq_clear /
snd_seq_oss_readq_free

write to 0xffff8881069fe608 of 4 bytes by task 120516 on cpu 0:
  snd_seq_oss_readq_free+0x6c/0x80
  snd_seq_oss_read+0xcb/0x250
  odev_read+0x38/0x60
  vfs_read+0xff/0x600
  ksys_read+0xb4/0x140
  __x64_sys_read+0x46/0x60
  do_syscall_64+0xbb/0x2f0
  entry_SYSCALL_64_after_hwframe+0x77/0x7f

read to 0xffff8881069fe608 of 4 bytes by task 120517 on cpu 1:
  snd_seq_oss_readq_clear+0x1f/0x90
  snd_seq_oss_reset+0xa7/0xf0
  snd_seq_oss_ioctl+0x6f6/0x7e0
  odev_ioctl+0x56/0xc0
  __x64_sys_ioctl+0xd1/0x120
  do_syscall_64+0xbb/0x2f0
  entry_SYSCALL_64_after_hwframe+0x77/0x7f

value changed: 0x00000001 -> 0x00000000

## References
- https://git.kernel.org/stable/c/287d506d4e0865918cec82bb1361f283a08c979b
- https://git.kernel.org/stable/c/43e10709b1ba288bcbabb9b9cb6e518b2a5d8506
- https://git.kernel.org/stable/c/49ce92d207820f588b0406add82f053decfbe5d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80628.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80628
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
