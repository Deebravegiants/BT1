# [H] ALSA: pcm: fix use-after-free on linked stream runtime in snd_pcm_drain()

## Summary
Severity: High
Advisory: CVE-2026-43437
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43437
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.253, >=5.11.0 <5.15.220, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: fix use-after-free on linked stream runtime in snd_pcm_drain()

In the drain loop, the local variable 'runtime' is reassigned to a
linked stream's runtime (runtime = s->runtime at line 2157).  After
releasing the stream lock at line 2169, the code accesses
runtime->no_period_wakeup, runtime->rate, and runtime->buffer_size
(lines 2170-2178) — all referencing the linked stream's runtime without
any lock or refcount protecting its lifetime.

A concurrent close() on the linked stream's fd triggers
snd_pcm_release_substream() → snd_pcm_drop() → pcm_release_private()
→ snd_pcm_unlink() → snd_pcm_detach_substream() → kfree(runtime).
No synchronization prevents kfree(runtime) from completing while the
drain path dereferences the stale pointer.

Fix by caching the needed runtime fields (no_period_wakeup, rate,
buffer_size) into local variables while still holding the stream lock,
and using the cached values after the lock is released.

## References
- https://git.kernel.org/stable/c/4a758e9a1f5ed722f83c4dd35f867fe811553bcb
- https://git.kernel.org/stable/c/629cf09464cf98670996ea5c191dc9743e6f3f00
- https://git.kernel.org/stable/c/9b1dbd69ba6f8f8c69bc7b77c2ce3b9c6ed05ba6
- https://git.kernel.org/stable/c/9baee36e8c5443411c4629afabafaff8a46a23fd
- https://git.kernel.org/stable/c/ae8f8d30d334bad5b1b3cdb1eb8a0b771f55e432
- https://git.kernel.org/stable/c/c2f64e05a0587a83ec42dbd6b7a7ded79b2ff694
- https://git.kernel.org/stable/c/f2cb2e0d27fb925c73a78f0ce7d6dbf68d3747c1
- https://git.kernel.org/stable/c/fc71f888994569f87d5bee20b1ac6c9c1e3a7a79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43437.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
