# [H] dm thin: make get_first_thin use rcu-safe list first function

## Summary
Severity: High
Advisory: CVE-2025-21664
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-21664
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm thin: make get_first_thin use rcu-safe list first function

The documentation in rculist.h explains the absence of list_empty_rcu()
and cautions programmers against relying on a list_empty() ->
list_first() sequence in RCU safe code.  This is because each of these
functions performs its own READ_ONCE() of the list head.  This can lead
to a situation where the list_empty() sees a valid list entry, but the
subsequent list_first() sees a different view of list head state after a
modification.

In the case of dm-thin, this author had a production box crash from a GP
fault in the process_deferred_bios path.  This function saw a valid list
head in get_first_thin() but when it subsequently dereferenced that and
turned it into a thin_c, it got the inside of the struct pool, since the
list was now empty and referring to itself.  The kernel on which this
occurred printed both a warning about a refcount_t being saturated, and
a UBSAN error for an out-of-bounds cpuid access in the queued spinlock,
prior to the fault itself.  When the resulting kdump was examined, it
was possible to see another thread patiently waiting in thin_dtr's
synchronize_rcu.

The thin_dtr call managed to pull the thin_c out of the active thins
list (and have it be the last entry in the active_thins list) at just
the wrong moment which lead to this crash.

Fortunately, the fix here is straight forward.  Switch get_first_thin()
function to use list_first_or_null_rcu() which performs just a single
READ_ONCE() and returns NULL if the list is already empty.

This was run against the devicemapper test suite's thin-provisioning
suites for delete and suspend and no regressions were observed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/12771050b6d059eea096993bf2001da9da9fddff
- https://git.kernel.org/stable/c/6b305e98de0d225ccebfb225730a9f560d28ecb0
- https://git.kernel.org/stable/c/802666a40c71a23542c43a3f87e3a2d0f4e8fe45
- https://git.kernel.org/stable/c/80f130bfad1dab93b95683fc39b87235682b8f72
- https://git.kernel.org/stable/c/cbd0d5ecfa390ac29c5380200147d09c381b2ac6
- https://git.kernel.org/stable/c/cd30a3960433ec2db94b3689752fa3c5df44d649
- https://git.kernel.org/stable/c/ec037fe8c0d0f6140e3d8a49c7b29cb5582160b8
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21664.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21664
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
