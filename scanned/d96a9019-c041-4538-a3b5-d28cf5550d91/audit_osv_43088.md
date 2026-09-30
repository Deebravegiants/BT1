# [H] md/raid1: fix writes_pending and barrier reference leaks on write failures

## Summary
Severity: High
Advisory: CVE-2026-72440
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72440
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid1: fix writes_pending and barrier reference leaks on write failures

raid1_make_request() acquires a writes_pending reference with
md_write_start() before calling raid1_write_request(). Several failure
paths in raid1_write_request() complete the bio and return without
reaching the normal write completion path, causing the corresponding
md_write_end() to be skipped.

Make raid1_write_request() return a status indicating whether the write
request was successfully queued. This allows raid1_make_request() to
call md_write_end() when raid1_write_request() fails.

Additionally, if wait_blocked_rdev() fails after wait_barrier()
succeeds, the associated barrier reference is not released.

Call allow_barrier() before returning from that path to keep the barrier
accounting balanced.

## References
- https://git.kernel.org/stable/c/8e065a1602511282fc0da2dc89445e0eb71a681c
- https://git.kernel.org/stable/c/bffbbfcbd9393e315a7a4286dcd70e875265db9a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
