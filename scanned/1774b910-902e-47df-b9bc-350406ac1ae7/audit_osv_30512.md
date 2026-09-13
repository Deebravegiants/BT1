# [H] mm: resolve faulty mmap_region() error path behaviour

## Summary
Severity: High
Advisory: CVE-2024-53096
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-53096
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.119, >=6.1.0 <6.6.63

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: resolve faulty mmap_region() error path behaviour

The mmap_region() function is somewhat terrifying, with spaghetti-like
control flow and numerous means by which issues can arise and incomplete
state, memory leaks and other unpleasantness can occur.

A large amount of the complexity arises from trying to handle errors late
in the process of mapping a VMA, which forms the basis of recently
observed issues with resource leaks and observable inconsistent state.

Taking advantage of previous patches in this series we move a number of
checks earlier in the code, simplifying things by moving the core of the
logic into a static internal function __mmap_region().

Doing this allows us to perform a number of checks up front before we do
any real work, and allows us to unwind the writable unmap check
unconditionally as required and to perform a CONFIG_DEBUG_VM_MAPLE_TREE
validation unconditionally also.

We move a number of things here:

1. We preallocate memory for the iterator before we call the file-backed
   memory hook, allowing us to exit early and avoid having to perform
   complicated and error-prone close/free logic. We carefully free
   iterator state on both success and error paths.

2. The enclosing mmap_region() function handles the mapping_map_writable()
   logic early. Previously the logic had the mapping_map_writable() at the
   point of mapping a newly allocated file-backed VMA, and a matching
   mapping_unmap_writable() on success and error paths.

   We now do this unconditionally if this is a file-backed, shared writable
   mapping. If a driver changes the flags to eliminate VM_MAYWRITE, however
   doing so does not invalidate the seal check we just performed, and we in
   any case always decrement the counter in the wrapper.

   We perform a debug assert to ensure a driver does not attempt to do the
   opposite.

3. We also move arch_validate_flags() up into the mmap_region()
   function. This is only relevant on arm64 and sparc64, and the check is
   only meaningful for SPARC with ADI enabled. We explicitly add a warning
   for this arch if a driver invalidates this check, though the code ought
   eventually to be fixed to eliminate the need for this.

With all of these measures in place, we no longer need to explicitly close
the VMA on error paths, as we place all checks which might fail prior to a
call to any driver mmap hook.

This eliminates an entire class of errors, makes the code easier to reason
about and more robust.

## References
- https://git.kernel.org/stable/c/43323a4e5b3f8ccc08e2f835abfdc7ee9da8f6ed
- https://git.kernel.org/stable/c/44f48eb9a6051826227bbd375446064fb2a43c6c
- https://git.kernel.org/stable/c/52c81fd0f5a8bf8032687b94ccf00d13b44cc5c8
- https://git.kernel.org/stable/c/5de195060b2e251a835f622759550e6202167641
- https://git.kernel.org/stable/c/bdc136e2b05fabcd780fe5f165d154eb779dfcb0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://project-zero.issues.chromium.org/issues/374117290
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53096.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
