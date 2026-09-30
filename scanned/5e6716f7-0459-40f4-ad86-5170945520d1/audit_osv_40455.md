# [H] ALSA: PCM: Fix wait queue list corruption in snd_pcm_drain() on linked streams

## Summary
Severity: High
Advisory: CVE-2026-53242
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53242
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.259, >=5.11.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: PCM: Fix wait queue list corruption in snd_pcm_drain() on linked streams

snd_pcm_drain() uses init_waitqueue_entry which does not clear
entry.prev/next, and add_wait_queue with a conditional
remove_wait_queue that is skipped when to_check is no longer
in the group after concurrent UNLINK.  The orphaned wait entry
remains on the unlinked substream sleep queue.  On the next
drain iteration, add_wait_queue adds the entry to a new queue
while still linked on the old one, corrupting both lists.  A
subsequent wake_up dereferences NULL at the func pointer
(mapped from the spinlock at offset 0 of the misinterpreted
wait_queue_head_t), causing a kernel panic.

Replace init_waitqueue_entry/add_wait_queue/conditional
remove_wait_queue with init_wait_entry/prepare_to_wait/
finish_wait.  init_wait_entry clears prev/next via
INIT_LIST_HEAD on each iteration and sets
autoremove_wake_function which auto-removes the entry on
wake-up.  finish_wait safely handles both the already-removed
and still-queued cases.

## References
- https://git.kernel.org/stable/c/06eca2235a3fd281dddf25b0a97772b25b5bb573
- https://git.kernel.org/stable/c/7c71a9522555ff137a9ca36b15d759ca04d84788
- https://git.kernel.org/stable/c/88fe2e3658726cb21ff2dcf9770bf672f9b9d31b
- https://git.kernel.org/stable/c/b053fcd8912f06c30f932f5b8ec41c72de474695
- https://git.kernel.org/stable/c/cac5bf3500ee6422cf64e0df0b5daeecfed42917
- https://git.kernel.org/stable/c/cd98837db15f323463b8df07282ac723bd5c3fed
- https://git.kernel.org/stable/c/d68b621bb5a48051932f1017a6e1bc9b18f854d0
- https://git.kernel.org/stable/c/d842f26a167e77a36f3ed333b9fa99d36ef99fe6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
