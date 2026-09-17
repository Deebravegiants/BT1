# [C] nfsd: fix possible badness in FREE_STATEID

## Summary
Severity: Critical
Advisory: CVE-2024-50043
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50043
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix possible badness in FREE_STATEID

When multiple FREE_STATEIDs are sent for the same delegation stateid,
it can lead to a possible either use-after-free or counter refcount
underflow errors.

In nfsd4_free_stateid() under the client lock we find a delegation
stateid, however the code drops the lock before calling nfs4_put_stid(),
that allows another FREE_STATE to find the stateid again. The first one
will proceed to then free the stateid which leads to either
use-after-free or decrementing already zeroed counter.

## References
- https://git.kernel.org/stable/c/7ca9e472ce5c67daa3188a348ece8c02a0765039
- https://git.kernel.org/stable/c/c88c150a467fcb670a1608e2272beeee3e86df6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50043.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
