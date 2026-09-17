# [M] blk-cgroup: Reinit blkg_iostat_set after clearing in blkcg_reset_stats()

## Summary
Severity: Medium
Advisory: CVE-2023-53421
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53421
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.258, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: Reinit blkg_iostat_set after clearing in blkcg_reset_stats()

When blkg_alloc() is called to allocate a blkcg_gq structure
with the associated blkg_iostat_set's, there are 2 fields within
blkg_iostat_set that requires proper initialization - blkg & sync.
The former field was introduced by commit 3b8cc6298724 ("blk-cgroup:
Optimize blkcg_rstat_flush()") while the later one was introduced by
commit f73316482977 ("blk-cgroup: reimplement basic IO stats using
cgroup rstat").

Unfortunately those fields in the blkg_iostat_set's are not properly
re-initialized when they are cleared in v1's blkcg_reset_stats(). This
can lead to a kernel panic due to NULL pointer access of the blkg
pointer. The missing initialization of sync is less problematic and
can be a problem in a debug kernel due to missing lockdep initialization.

Fix these problems by re-initializing them after memory clearing.

## References
- https://git.kernel.org/stable/c/0561aa6033dd181594116d705c41fc16e97161a2
- https://git.kernel.org/stable/c/3d2af77e31ade05ff7ccc3658c3635ec1bea0979
- https://git.kernel.org/stable/c/58c135513562698f222a58ba07dbdfcfb268aa0d
- https://git.kernel.org/stable/c/892faa76be894d324bf48b12a55c7af7be2bad83
- https://git.kernel.org/stable/c/abbce7f82613ea5eeefd0fc3c1c8e449b9cef2a2
- https://git.kernel.org/stable/c/b0d26283af612b9e0cc3188b0b88ad7fdea447e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53421.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53421
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
