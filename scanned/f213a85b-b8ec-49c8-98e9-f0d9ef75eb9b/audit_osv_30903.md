# [H] s390/cpum_sf: Fix and protect memory allocation of SDBs with mutex

## Summary
Severity: High
Advisory: CVE-2024-56706
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56706
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/cpum_sf: Fix and protect memory allocation of SDBs with mutex

Reservation of the PMU hardware is done at first event creation
and is protected by a pair of mutex_lock() and mutex_unlock().
After reservation of the PMU hardware the memory
required for the PMUs the event is to be installed on is
allocated by allocate_buffers() and alloc_sampling_buffer().
This done outside of the mutex protection.
Without mutex protection two or more concurrent invocations of
perf_event_init() may run in parallel.
This can lead to allocation of Sample Data Blocks (SDBs)
multiple times for the same PMU.
Prevent this and protect memory allocation of SDBs by
mutex.

## References
- https://git.kernel.org/stable/c/4b3bdfa89635db6a53e02955548bd07bebcae233
- https://git.kernel.org/stable/c/f55bd479d8663a4a4e403b3d308d3d1aa33d92df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56706.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56706
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
