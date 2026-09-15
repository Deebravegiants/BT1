# [C] KVM: arm64: vgic-its: Drop the translation cache reference only for the erased entry

## Summary
Severity: Critical
Advisory: CVE-2026-46316
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46316
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic-its: Drop the translation cache reference only for the erased entry

vgic_its_invalidate_cache() walks the per-ITS translation cache with
xa_for_each() and drops the cache's reference on each entry with
vgic_put_irq(). It puts the iterated pointer, though, rather than the
value returned by xa_erase().

The function is called from contexts that do not exclude one another: the
ITS command handlers hold its_lock, the GITS_CTLR write path holds
cmd_lock, and the path that clears EnableLPIs in a redistributor's
GICR_CTLR holds neither. Two or more of them can drain the same cache
concurrently, and if each one observes the same entry, erases it and then
puts it, the single reference the cache holds on that entry is dropped
more than once. The entry can then be freed while an ITE still maps it.

xa_erase() is atomic and returns the previous entry, so put only the entry
that this context actually removed. The cache reference is then dropped
exactly once per entry even when the invalidations run concurrently, and
the behavior is unchanged when only one context runs.

## References
- https://git.kernel.org/stable/c/13031fb6b8357fbbcded2a7f4cba73e4781ee594
- https://git.kernel.org/stable/c/2bbc395e81bd29c543a0529a678327e932a7ec69
- https://git.kernel.org/stable/c/9121f4605ab94969f62d1b5714ca3c6c69bd202f
- https://git.kernel.org/stable/c/b7b72e88046328c9fdc638fe887d4240257dd5dc
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46316.json
- https://access.redhat.com/errata/RHSA-2026:34911
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:38902
- https://access.redhat.com/errata/RHSA-2026:39371
- https://access.redhat.com/errata/RHSA-2026:40764
- https://access.redhat.com/errata/RHSA-2026:40779
- https://access.redhat.com/errata/RHSA-2026:40787
- https://access.redhat.com/errata/RHSA-2026:44231
- https://access.redhat.com/security/cve/CVE-2026-46316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46316.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46316
- https://bugzilla.redhat.com/show_bug.cgi?id=2486982
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
