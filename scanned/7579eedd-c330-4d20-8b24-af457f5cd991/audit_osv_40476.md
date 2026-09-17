# [H] iommu/vt-d: Avoid NULL pointer dereference or refcount corruption

## Summary
Severity: High
Advisory: CVE-2026-53281
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53281
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Avoid NULL pointer dereference or refcount corruption

Commit 60f030f7418d ("iommu/vt-d: Avoid use of NULL after WARN_ON_ONCE")
fixed a NULL pointer dereference in an unlikely situation partly.

If dev_pasid is not found in the dev_pasids list, it remains NULL.
However, the teardown operations are executed unconditionally, this lead
to a NULL pointer dereference or refcount corruption.

If the domain was never attached to this IOMMU, info will be NULL, which
would cause an immediate dereference when checking --info->refcnt.

Even if info is not NULL, decrementing the refcount without having removed
a valid PASID might unbalance the count. This could lead to premature
dropping of the refcount to 0, potentially causing a use-after-free for the
remaining active devices sharing the domain.

Fix it by returning early if dev_pasid is NULL, before executing the
teardown operations.

Issue found by AI review and suggested by Kevin Tian.
https://sashiko.dev/#/patchset/20260421031347.1408890-1-zhenzhong.duan%40intel.com

## References
- https://git.kernel.org/stable/c/79ea2feb917b05366b49d85573c9c5331f043b2c
- https://git.kernel.org/stable/c/9022cb9ac0c2a72a57fa8ebf92ac74f953ca0153
- https://git.kernel.org/stable/c/cdfe3c9f2c9e28a8651ee463c88ad191ced2f840
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53281.json
- https://access.redhat.com/errata/RHSA-2026:47017
- https://access.redhat.com/errata/RHSA-2026:47040
- https://access.redhat.com/security/cve/CVE-2026-53281
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53281.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53281
- https://bugzilla.redhat.com/show_bug.cgi?id=2493728
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
