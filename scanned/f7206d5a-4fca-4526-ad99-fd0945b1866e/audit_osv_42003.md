# [H] perf/aux: Fix page UAF in map_range()

## Summary
Severity: High
Advisory: CVE-2026-64300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64300
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/aux: Fix page UAF in map_range()

map_range() reads rb->aux_pages[], rb->aux_nr_pages and rb->aux_pgoff via
perf_mmap_to_page() while holding only event->mmap_mutex. Those fields are
serialized by rb->aux_mutex, and mmap_mutex is per event.

Thus, two events sharing one rb via PERF_EVENT_IOC_SET_OUTPUT can race
rb_alloc_aux() with map_range(), leading to a page-UAF scenario as follows:

  CPU 0                           CPU 1
  =====                           =====
  rb_alloc_aux()                  map_range()
  [1]: allocate rb->aux_pages[0]
  [2]: rb->aux_nr_pages++
                                  [3]: perf_mmap_to_page()
                                         returns rb->aux_pages[0]
                                  [4]: map it as VM_PFNMAP
  [5]: rb->aux_pgoff = 1

  munmap the page
  [6]: free rb->aux_pages[0]

Pages mapped as VM_PFNMAP have no refcount protection, so CPU 1 holds a
mapping to a freed physical frame.

Fix this by taking rb->aux_mutex across the page walk in map_range().

## References
- https://git.kernel.org/stable/c/0cff05bd2186020f8706233e261016d149cc24db
- https://git.kernel.org/stable/c/5948aaf64f81f217a25dcc2bf6c0779bca19566c
- https://git.kernel.org/stable/c/c8b7e113f7b61eef2f017e6329c27c2331058c5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64300.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
