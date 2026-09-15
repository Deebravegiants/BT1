# [H] kernel: be more careful about dup_mmap() failures and uprobe registering

## Summary
Severity: High
Advisory: CVE-2025-21709
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21709
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.83, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernel: be more careful about dup_mmap() failures and uprobe registering

If a memory allocation fails during dup_mmap(), the maple tree can be left
in an unsafe state for other iterators besides the exit path.  All the
locks are dropped before the exit_mmap() call (in mm/mmap.c), but the
incomplete mm_struct can be reached through (at least) the rmap finding
the vmas which have a pointer back to the mm_struct.

Up to this point, there have been no issues with being able to find an
mm_struct that was only partially initialised.  Syzbot was able to make
the incomplete mm_struct fail with recent forking changes, so it has been
proven unsafe to use the mm_struct that hasn't been initialised, as
referenced in the link below.

Although 8ac662f5da19f ("fork: avoid inappropriate uprobe access to
invalid mm") fixed the uprobe access, it does not completely remove the
race.

This patch sets the MMF_OOM_SKIP to avoid the iteration of the vmas on the
oom side (even though this is extremely unlikely to be selected as an oom
victim in the race window), and sets MMF_UNSTABLE to avoid other potential
users from using a partially initialised mm_struct.

When registering vmas for uprobe, skip the vmas in an mm that is marked
unstable.  Modifying a vma in an unstable mm may cause issues if the mm
isn't fully initialised.

## References
- https://git.kernel.org/stable/c/64c37e134b120fb462fb4a80694bfb8e7be77b14
- https://git.kernel.org/stable/c/74c2471eb891a7dcb3874b21c106cda75f52be30
- https://git.kernel.org/stable/c/da139948aeda677ac09cc0e7d837f8a314de7d55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21709.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21709
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
