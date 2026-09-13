# [H] nfsd: clean up potential nfsd_file refcount leaks in COPY codepath

## Summary
Severity: High
Advisory: CVE-2023-53606
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53606
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.220, >=5.11.0 <5.15.154, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: clean up potential nfsd_file refcount leaks in COPY codepath

There are two different flavors of the nfsd4_copy struct. One is
embedded in the compound and is used directly in synchronous copies. The
other is dynamically allocated, refcounted and tracked in the client
struture. For the embedded one, the cleanup just involves releasing any
nfsd_files held on its behalf. For the async one, the cleanup is a bit
more involved, and we need to dequeue it from lists, unhash it, etc.

There is at least one potential refcount leak in this code now. If the
kthread_create call fails, then both the src and dst nfsd_files in the
original nfsd4_copy object are leaked.

The cleanup in this codepath is also sort of weird. In the async copy
case, we'll have up to four nfsd_file references (src and dst for both
flavors of copy structure). They are both put at the end of
nfsd4_do_async_copy, even though the ones held on behalf of the embedded
one outlive that structure.

Change it so that we always clean up the nfsd_file refs held by the
embedded copy structure before nfsd4_copy returns. Rework
cleanup_async_copy to handle both inter and intra copies. Eliminate
nfsd4_cleanup_intra_ssc since it now becomes a no-op.

## References
- https://git.kernel.org/stable/c/6ba434cb1a8d403ea9aad1b667c3ea3ad8b3191f
- https://git.kernel.org/stable/c/75b8c681c563ef7e85da6862354efc18d2a08b1b
- https://git.kernel.org/stable/c/8f565846fbe8182961498d4cbe618b15076a683b
- https://git.kernel.org/stable/c/b3169b6ffe036b549c296a9e71591d29a1fb3209
- https://git.kernel.org/stable/c/fd63299db8090307eae66f2aef17c8f00aafa0a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53606.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
