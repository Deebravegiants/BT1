# [H] perf/core: Fix refcount bug and potential UAF in perf_mmap

## Summary
Severity: High
Advisory: CVE-2026-23248
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23248
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Fix refcount bug and potential UAF in perf_mmap

Syzkaller reported a refcount_t: addition on 0; use-after-free warning
in perf_mmap.

The issue is caused by a race condition between a failing mmap() setup
and a concurrent mmap() on a dependent event (e.g., using output
redirection).

In perf_mmap(), the ring_buffer (rb) is allocated and assigned to
event->rb with the mmap_mutex held. The mutex is then released to
perform map_range().

If map_range() fails, perf_mmap_close() is called to clean up.
However, since the mutex was dropped, another thread attaching to
this event (via inherited events or output redirection) can acquire
the mutex, observe the valid event->rb pointer, and attempt to
increment its reference count. If the cleanup path has already
dropped the reference count to zero, this results in a
use-after-free or refcount saturation warning.

Fix this by extending the scope of mmap_mutex to cover the
map_range() call. This ensures that the ring buffer initialization
and mapping (or cleanup on failure) happens atomically effectively,
preventing other threads from accessing a half-initialized or
dying ring buffer.

## References
- https://git.kernel.org/stable/c/77de62ad3de3967818c3dbe656b7336ebee461d2
- https://git.kernel.org/stable/c/ac7ecb65af170a7fc193e7bd8be15dac84ec6a56
- https://git.kernel.org/stable/c/c27dea9f50ed525facb62ef647dddc4722456e07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23248.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
